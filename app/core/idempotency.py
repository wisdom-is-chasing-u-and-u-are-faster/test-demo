import time
from typing import Dict, Any, Optional

# In-memory sliding-window store for local runtime with fallback from Redis
_idempotency_cache: Dict[str, Dict[str, Any]] = {}
IDEMPOTENCY_WINDOW_SECONDS = 900  # 15 minutes


def get_cached_idempotent_response(idempotency_key: str) -> Optional[Dict[str, Any]]:
    """Checks if an idempotency key was previously processed within the 15-minute sliding window."""
    if not idempotency_key:
        return None

    entry = _idempotency_cache.get(idempotency_key)
    if not entry:
        return None

    # Check if expired
    if time.time() - entry["timestamp"] > IDEMPOTENCY_WINDOW_SECONDS:
        del _idempotency_cache[idempotency_key]
        return None

    return entry["response"]


def store_idempotent_response(idempotency_key: str, response_payload: Dict[str, Any]):
    """Stores response payload associated with an idempotency key."""
    if not idempotency_key:
        return

    _idempotency_cache[idempotency_key] = {
        "timestamp": time.time(),
        "response": response_payload
    }
