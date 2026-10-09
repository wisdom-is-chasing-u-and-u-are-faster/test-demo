import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.core.security import create_access_token


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes schema and seed database for the test session."""
    init_database()


@pytest.fixture
def client():
    """Provides a TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def underwriter_auth_headers():
    """Generates authorization headers for Underwriter role."""
    token = create_access_token(user_id="usr_und_001", email="underwriter@bank.com", role="Underwriter")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operator_auth_headers():
    """Generates authorization headers for Operator role."""
    token = create_access_token(user_id="usr_opr_001", email="operator@bank.com", role="Operator")
    return {"Authorization": f"Bearer {token}"}
