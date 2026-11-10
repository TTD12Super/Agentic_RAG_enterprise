"""Safe, structured identity failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IdentityError(Exception):
    """An expected authentication failure safe to expose at the HTTP boundary."""

    code: str
    status_code: int
    message: str
    retryable: bool = False
    retry_after: int | None = None
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)


AUTH_REQUIRED = IdentityError(
    code="AUTH_REQUIRED",
    status_code=401,
    message="Authentication required.",
)
AUTH_INVALID = IdentityError(
    code="AUTH_INVALID",
    status_code=401,
    message="Invalid authentication credentials.",
)
MFA_REQUIRED = IdentityError(
    code="MFA_REQUIRED",
    status_code=401,
    message="Additional authentication is required.",
)
AUTH_UNAVAILABLE = IdentityError(
    code="AUTH_UNAVAILABLE",
    status_code=503,
    message="Authentication is temporarily unavailable.",
    retryable=True,
)
REQUEST_INVALID = IdentityError(
    code="REQUEST_INVALID",
    status_code=400,
    message="The request is invalid.",
)


def rate_limited(retry_after: int) -> IdentityError:
    return IdentityError(
        code="RATE_LIMITED",
        status_code=429,
        message="Too many authentication attempts.",
        retryable=True,
        retry_after=retry_after,
    )
