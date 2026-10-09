import os
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.errors import validation_exception_handler
from app.db.init_db import init_database
from app.api.auth import router as auth_router
from app.api.loans import router as loans_router
from app.api.underwriter import router as underwriter_router
from app.api.transactions import router as transactions_router
from app.api.analytics import router as analytics_router
from app.api.audit import router as audit_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Explicit origins for enterprise zero-trust compliance)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://bank.internal"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception Handlers (RFC-7807 Compliance)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.on_event("startup")
def on_startup():
    """Initializes database schema and seed data on server startup."""
    init_database()


# Health Check Probe
@app.get("/health", tags=["Health"])
def health_check():
    """Service health and readiness probe."""
    return {
        "status": "UP",
        "service": "automated-loan-approval-system",
        "version": settings.VERSION
    }


# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(loans_router, prefix=settings.API_V1_STR)
app.include_router(underwriter_router, prefix=settings.API_V1_STR)
app.include_router(transactions_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)

# Static Asset & SPA Page Mounting
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if not os.path.exists(public_dir):
    public_dir = "public"

if os.path.exists(public_dir):
    pages_dir = os.path.join(public_dir, "pages")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir), name="pages")
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
