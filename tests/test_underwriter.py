from fastapi import status


def test_underwriter_worklist_retrieval(client, underwriter_auth_headers):
    """Validates that the underwriter worklist displays cases requiring manual review (ARCH-2415-AC2, AC4)."""
    response = client.get("/api/v1/underwriter/worklist", headers=underwriter_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_cases" in data
    assert "cases" in data
    assert len(data["cases"]) > 0


def test_underwriter_case_details(client, underwriter_auth_headers):
    """Validates fetching detailed case dossier with credit bureau and policy traces."""
    response = client.get("/api/v1/underwriter/cases/EXC-002", headers=underwriter_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "applicant" in data
    assert "credit_bureau_data" in data
    assert "policy_evaluations" in data


def test_underwriter_adjudicate_case_approval(client, underwriter_auth_headers):
    """Validates underwriter case adjudication and notice delivery (ARCH-2415-AC10)."""
    payload = {
        "action": "APPROVE",
        "notes": "Verified secondary assets. Income is stable.",
        "approved_amount": 28000.0,
        "approved_rate": 7.85,
        "reason_codes": ["UNDERWRITER_OVERRIDE"]
    }
    response = client.post("/api/v1/underwriter/cases/EXC-002/adjudicate",
                           json=payload, headers=underwriter_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["action"] == "APPROVE"
    assert data["status"] == "APPROVED"
    assert data["notice_generated"] is True
