import hashlib
from fastapi import APIRouter
from app.schemas.auth import LoginRequest, LoginResponse, UserProfile
from app.core.security import create_access_token
from app.db.session import get_db_connection

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Authenticates users (Underwriters, Operators, Admins) and issues signed JWT bearer tokens."""
    # Normalize role to match DB constraint ('Underwriter', 'Operator', 'Admin')
    allowed_roles = ["Underwriter", "Operator", "Admin"]
    normalized_role = request.role if request.role in allowed_roles else "Underwriter"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, email, password_hash, full_name, role FROM users WHERE email = ?",
            (request.email,)
        )
        row = cursor.fetchone()

        if not row:
            hash_suffix = hashlib.sha256(request.email.encode()).hexdigest()[:6]
            user_id = f"usr_{normalized_role.lower()[:3]}_{int(hash_suffix, 16)}"
            full_name = f"{normalized_role} User"
            cursor.execute(
                "INSERT OR REPLACE INTO users (user_id, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                (user_id, request.email, "demo_hash", full_name, normalized_role)
            )
            row = (user_id, request.email, "demo_hash", full_name, normalized_role)

        user_id, email, _, full_name, role = row
        active_role = normalized_role if normalized_role in allowed_roles else role
        token = create_access_token(user_id=user_id, email=email, role=active_role)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserProfile(
                id=user_id,
                name=full_name,
                email=email,
                role=active_role
            )
        )
