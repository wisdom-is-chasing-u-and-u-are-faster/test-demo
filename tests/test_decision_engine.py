from app.services.credit_bureau import bureau_gateway
from app.services.decision_engine import decision_engine


def test_credit_bureau_gateway_resilience():
    """Validates credit bureau inquiry with Experian/Equifax fallback logic (ARCH-2415-AC8)."""
    report = bureau_gateway.fetch_credit_report(
        ssn="123-45-6789",
        applicant_name="Test Applicant",
        annual_income=90000.0
    )
    assert report["status"] in ["SUCCESS", "SUCCESS_FALLBACK", "FALLBACK_MODEL"]
    assert 500 <= report["credit_score"] <= 850
    assert "revolving_utilization_pct" in report


def test_decision_engine_superprime_approval():
    """Validates deterministic decision engine approving high-score low-DTI profile (ARCH-2415-AC9)."""
    result = decision_engine.evaluate(
        annual_income=120000.0,
        loan_amount=20000.0,
        term_months=36,
        credit_score=780,
        delinquencies=0,
        revolving_util=15.0
    )
    assert result["decision"] == "APPROVED"
    assert result["approved_amount"] >= 20000.0
    assert result["interest_rate"] <= 6.5


def test_decision_engine_subprime_rejection():
    """Validates deterministic decision engine rejecting severe subprime score."""
    result = decision_engine.evaluate(
        annual_income=35000.0,
        loan_amount=30000.0,
        term_months=36,
        credit_score=550,
        delinquencies=3,
        revolving_util=85.0
    )
    assert result["decision"] == "REJECTED"
    assert len(result["reason_codes"]) > 0


def test_decision_engine_manual_review_trigger():
    """Validates deterministic decision engine routing borderline cases to underwriter worklist."""
    result = decision_engine.evaluate(
        annual_income=65000.0,
        loan_amount=35000.0,
        term_months=36,
        credit_score=645,
        delinquencies=0,
        revolving_util=55.0
    )
    assert result["decision"] == "MANUAL_REVIEW"
    assert "POL-SCORE-BORDERLINE" in result["reason_codes"] or "POL-DTI-ELEVATED" in result["reason_codes"]
