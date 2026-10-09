from fastapi import status


def test_operator_transaction_submission_success(client, operator_auth_headers):
    """Validates that authenticated users with 'Operator' role can submit transactions (ARCH-2415-AC15)."""
    payload = {
        "transaction_id": "txn_test_001",
        "tenant_id": "org_481878",
        "action": "INITIATE",
        "payload": {
            "entity_name": "Corporate KYC Submission",
            "amount": 50000.0,
            "currency": "USD"
        }
    }
    response = client.post("/api/v1/transactions", json=payload, headers=operator_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert "tracking_id" in data


def test_analytics_metrics_endpoint(client):
    """Validates telemetry and analytics metrics endpoint."""
    response = client.get("/api/v1/analytics/metrics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "stp_rate_pct" in data
    assert "p95_latency_sec" in data
    assert data["total_applications_today"] > 0
