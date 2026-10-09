from fastapi import APIRouter
from app.db.session import get_db_connection

router = APIRouter(prefix="/audit", tags=["Compliance Audit Ledger"])


@router.get("/ledger")
def get_audit_ledger(limit: int = 50):
    """Queries immutable Write-Once-Read-Many (WORM) compliance audit events."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT event_id, event_type, entity_id, actor, payload_hash, timestamp
            FROM audit_ledger
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        events = []
        for r in rows:
            events.append({
                "event_id": r[0],
                "event_type": r[1],
                "entity_id": r[2],
                "actor": r[3],
                "payload_hash": r[4],
                "timestamp": str(r[5])
            })

        return {
            "total_events": len(events),
            "events": events
        }
