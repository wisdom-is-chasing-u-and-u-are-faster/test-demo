import json
import time
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.underwriter import (
    WorklistResponse,
    WorklistItem,
    CaseAdjudicationRequest,
    CaseAdjudicationResponse
)
from app.core.security import get_current_user
from app.db.session import get_db_connection
from app.services.notifications import notification_dispatcher

router = APIRouter(prefix="/underwriter", tags=["Underwriter Portal"])


@router.get("/worklist", response_model=WorklistResponse)
def get_worklist(user: dict = Depends(get_current_user)):
    """Fetches list of loan application cases requiring manual underwriter adjudication."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT
                e.exception_id,
                e.application_id,
                a.applicant_first_name || ' ' || a.applicant_last_name AS applicant_name,
                a.loan_amount,
                c.credit_score,
                c.debt_to_income_ratio,
                e.risk_grade,
                e.trigger_reason,
                e.action_taken,
                a.created_at
            FROM underwriter_exceptions e
            JOIN loan_applications a ON e.application_id = a.application_id
            LEFT JOIN credit_reports c ON e.application_id = c.application_id
            ORDER BY a.created_at DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        items = []
        pending_count = 0
        for r in rows:
            exc_id, app_id, name, amount, score, dti, grade, trigger, action, submitted_at = r
            if action == "PENDING":
                status_label = "Pending Review"
                pending_count += 1
            elif action == "APPROVE":
                status_label = "Approved"
            else:
                status_label = "Rejected"

            items.append(WorklistItem(
                case_id=exc_id,
                application_id=app_id,
                applicant_name=name or "Unknown Applicant",
                loan_amount=float(amount or 0.0),
                credit_score=int(score or 650),
                dti_ratio=float(dti or 0.35),
                risk_grade=grade or "B",
                trigger_reason=trigger or "Manual Review Required",
                status=status_label,
                submitted_at=str(submitted_at or "2026-10-09")
            ))

        return WorklistResponse(
            total_cases=len(items),
            pending_review=pending_count,
            cases=items
        )


@router.get("/cases/{case_id}")
def get_case_details(case_id: str, user: dict = Depends(get_current_user)):
    """Fetches comprehensive case review dossier including credit bureau scores and policy rules."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.exception_id, e.application_id, e.risk_grade, e.trigger_reason, e.action_taken, e.notes,
                   a.applicant_first_name, a.applicant_last_name, a.ssn_masked, a.annual_income,
                   a.loan_amount, a.term_months, a.loan_purpose, a.email,
                   c.bureau_name, c.credit_score, c.delinquencies_24m,
                   c.revolving_utilization_pct, c.debt_to_income_ratio
            FROM underwriter_exceptions e
            JOIN loan_applications a ON e.application_id = a.application_id
            LEFT JOIN credit_reports c ON e.application_id = c.application_id
            WHERE e.exception_id = ? OR e.application_id = ?
            """,
            (case_id, case_id)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found.")

        (exc_id, app_id, grade, trigger, action, notes,
         f_name, l_name, ssn_masked, income,
         amount, term, purpose, email,
         bureau, score, delinq, util, dti) = row

        monthly_income = float(income or 60000) / 12.0
        monthly_debt = monthly_income * float(dti or 0.35)

        return {
            "case_id": exc_id,
            "application_id": app_id,
            "applicant": {
                "name": f"{f_name} {l_name}",
                "email": email,
                "masked_ssn": ssn_masked,
                "annual_income": float(income or 0.0),
                "monthly_debt": round(monthly_debt, 2)
            },
            "loan": {
                "amount": float(amount or 0.0),
                "term_months": int(term or 36),
                "purpose": purpose or "Personal"
            },
            "credit_bureau_data": {
                "bureau": bureau or "Experian",
                "credit_score": int(score or 650),
                "delinquencies_24m": int(delinq or 0),
                "revolving_utilization_pct": float(util or 30.0)
            },
            "policy_evaluations": [
                {
                    "rule_id": "POL-DTI-01",
                    "rule_name": "Debt-to-Income Ratio Threshold Check",
                    "result": "REVIEW" if (dti or 0.0) > 0.38 else "PASS",
                    "details": f"DTI {float(dti or 0.0):.1%} evaluation"
                },
                {
                    "rule_id": "POL-SCORE-02",
                    "rule_name": "Minimum Credit Bureau Score Filter",
                    "result": "PASS" if (score or 0) >= 620 else "REVIEW",
                    "details": f"Credit Bureau score is {score}"
                }
            ],
            "status": "PENDING_REVIEW" if action == "PENDING" else action,
            "notes": notes or ""
        }


@router.post("/cases/{case_id}/adjudicate", response_model=CaseAdjudicationResponse)
def adjudicate_case(
    case_id: str,
    request: CaseAdjudicationRequest,
    user: dict = Depends(get_current_user)
):
    """Underwriter adjudication action (APPROVE, REJECT, or REQUEST_INFO) with FCRA/ECOA dispatch."""
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    adjudicator_name = user.get("email", "underwriter@bank.com")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT exception_id, application_id FROM underwriter_exceptions "
            "WHERE exception_id = ? OR application_id = ?",
            (case_id, case_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' was not found.")

        exc_id, app_id = row

        # Determine canonical status and decision
        if request.action in ["APPROVE", "APPROVED"]:
            new_app_status = "APPROVED"
            canonical_decision = "APPROVED"
        elif request.action in ["REJECT", "REJECTED"]:
            new_app_status = "REJECTED"
            canonical_decision = "REJECTED"
        else:
            new_app_status = "UNDER_REVIEW"
            canonical_decision = "MANUAL_REVIEW"

        cursor.execute(
            """
            UPDATE underwriter_exceptions
            SET action_taken = ?, notes = ?, fcra_notice_sent = TRUE, adjudicated_at = ?
            WHERE exception_id = ?
            """,
            (request.action, request.notes, timestamp, exc_id)
        )

        cursor.execute(
            "UPDATE loan_applications SET status = ?, updated_at = ? WHERE application_id = ?",
            (new_app_status, timestamp, app_id)
        )

        # Update decision record with valid constraint value ('APPROVED', 'REJECTED', 'MANUAL_REVIEW')
        cursor.execute(
            """
            UPDATE decision_records
            SET decision = ?, approved_amount = ?, interest_rate = ?, reason_codes = ?
            WHERE application_id = ?
            """,
            (
                canonical_decision,
                request.approved_amount or 0.0,
                request.approved_rate or 0.0,
                json.dumps(request.reason_codes or []),
                app_id
            )
        )

        # WORM Audit Record
        hash_seed = f"{case_id}_{timestamp}"
        event_id = f"EVT-{str(hashlib.sha256(hash_seed.encode()).hexdigest()[:8]).upper()}"
        audit_payload = {
            "case_id": exc_id,
            "application_id": app_id,
            "action": request.action,
            "adjudicator": adjudicator_name,
            "notes": request.notes
        }
        payload_json = json.dumps(audit_payload)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        cursor.execute(
            """
            INSERT INTO audit_ledger (event_id, event_type, entity_id, actor, payload_hash, payload_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_id, "UNDERWRITER_ADJUDICATION", exc_id, adjudicator_name, payload_hash, payload_json)
        )

        # Fetch applicant info to dispatch notification
        cursor.execute(
            "SELECT applicant_first_name || ' ' || applicant_last_name, email "
            "FROM loan_applications WHERE application_id = ?",
            (app_id,)
        )
        app_user_row = cursor.fetchone()
        if app_user_row:
            applicant_name, applicant_email = app_user_row
            notification_dispatcher.dispatch_decision_notice(
                application_id=app_id,
                applicant_email=applicant_email,
                applicant_name=applicant_name,
                decision=new_app_status,
                approved_amount=request.approved_amount or 0.0,
                reason_codes=request.reason_codes or []
            )

        return CaseAdjudicationResponse(
            case_id=exc_id,
            action=request.action,
            status=new_app_status,
            adjudicated_by=adjudicator_name,
            adjudicated_at=timestamp,
            notice_generated=True
        )
