import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Automated Loan Approval System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 12-factor Dual Mode Environment Variable Bindings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./alas.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "alas-super-secret-enterprise-key-change-in-prod-2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    IDEMPOTENCY_TTL_SECONDS: int = 900  # 15 minutes window

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
