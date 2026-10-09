from fastapi import status


def test_auth_login_success(client):
    """Validates successful login and JWT token issuance."""
    payload = {
        "email": "underwriter@bank.com",
        "password": "",
        "role": "Underwriter"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "Underwriter"


def test_underwriter_portal_unauthorized_without_token(client):
    """Validates that underwriter portal endpoints reject unauthenticated access (ARCH-2415-AC3)."""
    response = client.get("/api/v1/underwriter/worklist")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
