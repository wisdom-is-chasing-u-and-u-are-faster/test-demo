from app.db.session import get_db_connection


def test_database_tables_exist():
    """Validates that all relational database tables exist in the schema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = [
            "users", "loan_applications", "credit_reports",
            "decision_records", "underwriter_exceptions",
            "audit_ledger", "transactions"
        ]
        for t in required_tables:
            assert t in tables, f"Expected table '{t}' was not found in database schema."


def test_seed_data_loaded():
    """Validates that initial seed data is present."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count >= 3, "Expected at least 3 initial seed users."

        cursor.execute("SELECT COUNT(*) FROM loan_applications")
        app_count = cursor.fetchone()[0]
        assert app_count >= 3, "Expected at least 3 initial seed applications."


def test_worm_audit_ledger_persistence():
    """Validates that audit ledger events are properly recorded (ARCH-2415-AC11)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO audit_ledger (event_id, event_type, entity_id, actor, payload_hash, payload_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("EVT-TEST-001", "TEST_EVENT", "ENT-001", "tester@bank.com", "dummy_hash", '{"status": "ok"}')
        )

        cursor.execute("SELECT event_type, payload_hash FROM audit_ledger WHERE event_id = 'EVT-TEST-001'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "TEST_EVENT"
        assert row[1] == "dummy_hash"
