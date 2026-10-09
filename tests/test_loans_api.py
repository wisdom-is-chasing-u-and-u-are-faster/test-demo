from fastapi import status


def test_submit_loan_application_success(client):
    """Validates public loan application intake form submission and decision (ARCH-2415-AC1)."""
    payload = {
        "applicant": {
            "first_name": "Jordan",
            "last_name": "Taylor",
            "email": "jordan.taylor@example.com",
            "phone": "555-0199",
            "ssn": "123-45-6789",
            "date_of_birth": "1994-06-20",
            "address": {
                "street": "100 Innovation Way",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601"
            }
        },
        "employment": {
            "employer_name": "Fintech Solutions",
            "job_title": "Lead Engineer",
            "annual_income": 130000.0,
            "employment_status": "Full-Time",
            "years_employed": 5
        },
        "loan": {
            "amount": 25000.0,
            "term_months": 36,
            "purpose": "Home Improvement"
        }
    }
    idempotency_key = "idemp_test_unique_001"
    response = client.post("/api/v1/loans/applications", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "application_id" in data
    assert data["status"] in ["APPROVED", "UNDER_REVIEW", "REJECTED"]
    assert "decision" in data
    assert data["decision"]["credit_score"] > 0

    # Test Idempotency: Duplicate submission with same key returns identical cached response (ARCH-2415-AC7)
    dup_response = client.post("/api/v1/loans/applications", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert dup_response.status_code == status.HTTP_201_CREATED
    assert dup_response.json()["application_id"] == data["application_id"]


def test_application_status_pii_masking(client):
    """Validates that SSN PII is masked as XXX-XX-1234 in status output (ARCH-2415-AC13)."""
    response = client.get("/api/v1/loans/applications/APP-2026-001")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "masked_ssn" in data
    assert data["masked_ssn"].startswith("XXX-XX-")
    assert "timeline" in data
    assert len(data["timeline"]) >= 3
