from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, List, Any
import time


def create_rfc7807_error_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    error_code: str = "ERR_GENERIC",
    invalid_params: Optional[List[Any]] = None
) -> JSONResponse:
    """Formats error responses adhering strictly to RFC-7807 problem details specification."""
    content: dict[str, Any] = {
        "type": f"https://api.alas.bank.internal/errors/{error_code.lower()}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "error_code": error_code,
        "timestamp": int(time.time())
    }
    if invalid_params:
        content["invalid_params"] = invalid_params
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Custom handler for pydantic request validation exceptions conforming to RFC-7807."""
    invalid_params = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Invalid field value")
        invalid_params.append({"name": loc, "reason": msg})

    return create_rfc7807_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        title="Invalid Request Payload",
        detail="The request body or parameters failed schema validation.",
        instance=str(request.url.path),
        error_code="ERR_REQ_INVALID",
        invalid_params=invalid_params
    )
