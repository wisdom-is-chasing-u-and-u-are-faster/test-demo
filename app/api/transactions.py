import time
import uuid
import json
import hashlib
from fastapi import APIRouter, Depends, status
from app.schemas.transaction import TransactionRequest, TransactionResponse
from app.core.security import require_roles
from app.db.session import get_db_connection

router = APIRouter(tags=["Transactions"])


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def submit_transaction(
    request: TransactionRequest,
    user: dict = Depends(require_roles(["Operator", "Admin"]))
):
    """Authenticated users with 'Operator' role submit transactions via POST /api/v1/transactions."""
    tracking_id = f"trk_{str(uuid.uuid4())[:8]}"
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Commit transaction to database (REQ-F-016)
        cursor.execute(
            """
            INSERT OR REPLACE INTO transactions (
                transaction_id, tenant_id, action, entity_name, amount, currency, status, tracking_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.transaction_id,
                request.tenant_id,
                request.action,
                request.payload.entity_name,
                request.payload.amount,
                request.payload.currency,
                "ACCEPTED",
                tracking_id,
                created_at
            )
        )

        # Log audit event to immutable compliance ledger (REQ-F-016)
        event_id = f"EVT-TXN-{str(uuid.uuid4())[:8].upper()}"
        payload_dict = request.model_dump() if hasattr(request, "model_dump") else request.dict()
        payload_json = json.dumps(payload_dict)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        actor = user.get("email", "operator@bank.com")

        cursor.execute(
            """
            INSERT OR REPLACE INTO audit_ledger (
                event_id, event_type, entity_id, actor, payload_hash, payload_json, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_id, "TRANSACTION_SUBMITTED", request.transaction_id, actor, payload_hash, payload_json, created_at)
        )

    return TransactionResponse(
        status="ACCEPTED",
        tracking_id=tracking_id,
        created_at=created_at,
        next_step="AWAITING_VERIFICATION"
    )
