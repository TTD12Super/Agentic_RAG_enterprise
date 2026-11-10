"""Trusted principal and internal identity records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Role(StrEnum):
    SYSTEM_ADMIN = "system_admin"
    WEBSITE_MANAGER = "website_manager"
    EMPLOYEE = "employee"
    CHAIRMAN = "chairman"


CANONICAL_ROLES = frozenset(role.value for role in Role)
MFA_ROLES = frozenset(
    {Role.SYSTEM_ADMIN.value, Role.WEBSITE_MANAGER.value, Role.CHAIRMAN.value}
)


def utc_z(value: datetime) -> str:
    """Render a UTC timestamp in the contract's RFC 3339 ``Z`` form."""

    return value.astimezone().isoformat().replace("+00:00", "Z")


class AuthenticatedPrincipal(BaseModel):
    """The only principal shape accepted by downstream backend components."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    user_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    roles: list[str] = Field(min_length=1)
    groups: list[str] = Field(default_factory=list)
    department_ids: list[str] = Field(default_factory=list)
    session_id: str = Field(min_length=1)
    auth_time: str = Field(min_length=1)

    @field_validator("roles")
    @classmethod
    def canonical_roles(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)) or not set(value) <= CANONICAL_ROLES:
            raise ValueError("roles must be unique canonical roles")
        return sorted(value)


@dataclass(frozen=True)
class IdentityRecord:
    """Server-side identity data; never constructed from request claims."""

    user_id: str
    tenant_id: str
    email: str
    password_hash: str
    roles: tuple[str, ...]
    groups: tuple[str, ...] = ()
    department_ids: tuple[str, ...] = ()
    active: bool = True
    mfa_code_hash: str | None = None

    @property
    def requires_mfa(self) -> bool:
        return bool(set(self.roles) & MFA_ROLES)


@dataclass
class SessionRecord:
    """Server-side session metadata keyed by a hash of the bearer token."""

    session_id: str
    user_id: str
    tenant_id: str
    token_hash: str
    auth_time: datetime
    last_seen_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


def normalize_roles(roles: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(sorted(set(roles)))
    if not normalized or not set(normalized) <= CANONICAL_ROLES:
        raise ValueError("roles must contain only canonical roles")
    return normalized
