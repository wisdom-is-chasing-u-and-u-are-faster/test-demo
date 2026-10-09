from typing import Dict, Any


class DecisionEngine:
    """Stateless, deterministic credit decision policy engine implementing DMN/Drools-compatible rules."""

    def evaluate(
        self,
        annual_income: float,
        loan_amount: float,
        term_months: int,
        credit_score: int,
        delinquencies: int,
        revolving_util: float
    ) -> Dict[str, Any]:
        """Evaluates loan eligibility against credit rules and policies."""
        monthly_income = annual_income / 12.0
        # Estimated monthly payment (simple interest amortization)
        monthly_payment = loan_amount / float(term_months)
        estimated_dti = (monthly_payment + (annual_income * 0.15 / 12.0)) / monthly_income

        reason_codes = []
        policy_trace = []

        # Rule 1: Hard rejection on severe subprime score or multiple delinquencies
        if credit_score < 600 or delinquencies >= 2:
            reason_codes.append("ECOA-01: Insufficient credit score or excessive past delinquency history")
            policy_trace.append({"rule": "POL-SCORE-MIN", "result": "FAIL", "score": credit_score})
            return {
                "decision": "REJECTED",
                "approved_amount": 0.0,
                "interest_rate": 0.0,
                "credit_score": credit_score,
                "dti_ratio": round(estimated_dti, 4),
                "reason_codes": reason_codes,
                "policy_trace": policy_trace
            }

        # Rule 2: Manual Underwriter Review for borderline credit score or elevated DTI
        if credit_score < 680 or estimated_dti > 0.40 or loan_amount > 45000:
            trigger_reasons = []
            if credit_score < 680:
                trigger_reasons.append(f"Credit score {credit_score} is below STP threshold 680")
                reason_codes.append("POL-SCORE-BORDERLINE")
            if estimated_dti > 0.40:
                trigger_reasons.append(f"DTI {estimated_dti:.1%} exceeds automated guideline 40.0%")
                reason_codes.append("POL-DTI-ELEVATED")
            if loan_amount > 45000:
                trigger_reasons.append(f"Loan amount ${loan_amount:,.2f} exceeds straight-through limit $45,000")
                reason_codes.append("POL-AMOUNT-HIGH")

            policy_trace.append({
                "rule": "POL-MANUAL-REVIEW-GATE",
                "result": "REVIEW",
                "triggers": trigger_reasons
            })

            return {
                "decision": "MANUAL_REVIEW",
                "approved_amount": 0.0,
                "interest_rate": 0.0,
                "credit_score": credit_score,
                "dti_ratio": round(estimated_dti, 4),
                "trigger_reason": "; ".join(trigger_reasons),
                "reason_codes": reason_codes,
                "policy_trace": policy_trace
            }

        # Rule 3: Automated STP Approval for prime risk profiles
        # Base interest rate tiers based on score
        if credit_score >= 760:
            rate = 5.75
            max_amount = min(loan_amount * 1.25, 100000.0)
            reason_codes.append("POL-TIER-SUPERPRIME")
        elif credit_score >= 720:
            rate = 6.45
            max_amount = loan_amount
            reason_codes.append("POL-TIER-PRIME")
        else:
            rate = 7.85
            max_amount = loan_amount
            reason_codes.append("POL-TIER-STANDARD")

        policy_trace.append({"rule": "POL-STP-APPROVE", "result": "PASS", "rate": rate})

        return {
            "decision": "APPROVED",
            "approved_amount": round(max_amount, 2),
            "interest_rate": rate,
            "credit_score": credit_score,
            "dti_ratio": round(estimated_dti, 4),
            "reason_codes": reason_codes,
            "policy_trace": policy_trace
        }


decision_engine = DecisionEngine()
