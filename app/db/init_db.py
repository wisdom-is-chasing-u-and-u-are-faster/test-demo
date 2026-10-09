import sys
from pathlib import Path

# Ensure app package is importable when executed standalone
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from app.db.session import get_db_connection  # noqa: E402


def init_database():
    """Initializes schema and baseline seed records upon service startup."""
    schema_path = base_dir / "db" / "schema.sql"
    seed_path = base_dir / "db" / "seed.sql"

    if not schema_path.exists():
        schema_path = Path("db/schema.sql")
    if not seed_path.exists():
        seed_path = Path("db/seed.sql")

    with get_db_connection() as conn:
        if schema_path.exists():
            schema_sql = schema_path.read_text(encoding="utf-8")
            conn.executescript(schema_sql)

        # Check if users table is populated
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0 and seed_path.exists():
            seed_sql = seed_path.read_text(encoding="utf-8")
            conn.executescript(seed_sql)


if __name__ == "__main__":
    init_database()
    print("Database schema and seed initialized successfully.")
