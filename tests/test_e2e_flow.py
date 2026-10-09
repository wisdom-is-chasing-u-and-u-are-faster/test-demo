from fastapi import status


def test_rfc7807_validation_error_format(client):
    """Validates that invalid request payloads return RFC-7807 problem details (ARCH-2415-AC14)."""
    # Invalid payload: missing mandatory applicant details
    invalid_payload = {
        "loan": {
            "amount": -500.0,
            "term_months": 0
        }
    }
    response = client.post("/api/v1/loans/applications", json=invalid_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert data["status"] == 400
    assert "detail" in data
    assert "invalid_params" in data


def test_complete_end_to_end_origination_flow(client, underwriter_auth_headers):
    """Validates full end-to-end flow: Intake -> Decision -> Underwriter Review -> Adjudication."""
    # 1. Submit Borderline Application
    intake_payload = {
        "applicant": {
            "first_name": "Taylor",
            "last_name": "Reed",
            "email": "taylor.reed@example.com",
            "phone": "555-0988",
            "ssn": "456-78-9012",
            "date_of_birth": "1991-03-10",
            "address": {
                "street": "123 Market St",
                "city": "Seattle",
                "state": "WA",
                "zip_code": "98101"
            }
        },
        "employment": {
            "employer_name": "Tech Startup",
            "job_title": "Product Designer",
            "annual_income": 62000.0,
            "employment_status": "Full-Time",
            "years_employed": 2
        },
        "loan": {
            "amount": 35000.0,
            "term_months": 48,
            "purpose": "Debt Consolidation"
        }
    }
    submit_res = client.post("/api/v1/loans/applications", json=intake_payload)
    assert submit_res.status_code == status.HTTP_201_CREATED
    app_id = submit_res.json()["application_id"]

    # 2. Check Status
    status_res = client.get(f"/api/v1/loans/applications/{app_id}")
    assert status_res.status_code == status.HTTP_200_OK
    assert status_res.json()["masked_ssn"] == "XXX-XX-9012"

    # 3. Retrieve Underwriter Worklist
    worklist_res = client.get("/api/v1/underwriter/worklist", headers=underwriter_auth_headers)
    assert worklist_res.status_code == status.HTTP_200_OK

    # 4. Adjudicate Application
    adj_payload = {
        "action": "APPROVE",
        "notes": "E2E automated flow approval.",
        "approved_amount": 35000.0,
        "approved_rate": 7.5
    }
    adj_res = client.post(
        f"/api/v1/underwriter/cases/{app_id}/adjudicate",
        json=adj_payload,
        headers=underwriter_auth_headers)
    assert adj_res.status_code == status.HTTP_200_OK
    assert adj_res.json()["status"] == "APPROVED"
