from fastapi import status


def test_health_check_endpoint(client):
    """Validates that GET /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "UP"


def test_static_root_mount(client):
    """Validates that GET / serves public/index.html cleanly without 404."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Automated Loan Approval System" in response.text


def test_static_pages_mount(client):
    """Validates that all UI pages are mounted and accessible under /pages/."""
    pages = [
        "login.html", "loan-intake.html", "status-check.html",
        "underwriter-dashboard.html", "case-review.html", "analytics-dashboard.html"
    ]
    for page in pages:
        response = client.get(f"/pages/{page}")
        assert response.status_code == status.HTTP_200_OK, f"Failed to serve /pages/{page}"
        assert "<html" in response.text.lower()


def test_client_api_and_i18n_assets(client):
    """Validates that client API script and i18n localization dictionary exist and are served."""
    api_js = client.get("/js/api.js")
    assert api_js.status_code == status.HTTP_200_OK
    assert "AlasApi" in api_js.text

    i18n_js = client.get("/js/i18n.js")
    assert i18n_js.status_code == status.HTTP_200_OK
    assert "es-US" in i18n_js.text
    assert "en-US" in i18n_js.text
