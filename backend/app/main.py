"""FastAPI application shell.

Feature routes are added by their owning tasks after the shared contracts are
implemented. The current shell exposes dependency-free liveness and identity
routes; data, provider and feature workflows remain downstream work.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.identity import router as identity_router
from .core.config import get_settings
from .identity.errors import IdentityError
from .observability import CorrelationContext

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Idempotency-Key",
        "Traceparent",
        "X-Anonymous-Session",
        "X-Request-ID",
    ],
    expose_headers=["Retry-After", "Traceparent", "X-Request-ID"],
)
app.include_router(identity_router, prefix=settings.api_prefix)


@app.exception_handler(IdentityError)
async def identity_error_handler(
    request: Request, error: IdentityError
) -> JSONResponse:
    """Return a safe problem envelope without credentials or internal details."""

    context = CorrelationContext.from_headers(request.headers)
    headers = context.response_headers
    if error.retry_after is not None:
        headers["Retry-After"] = str(error.retry_after)
    return JSONResponse(
        status_code=error.status_code,
        content={
            "code": error.code,
            "message": error.message,
            "request_id": context.request_id,
            "retryable": error.retryable,
        },
        headers=headers,
        media_type="application/problem+json",
    )


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    """Report process liveness without querying external dependencies."""

    return {"status": "ok"}
