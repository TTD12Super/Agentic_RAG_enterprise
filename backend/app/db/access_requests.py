"""Durable access-request storage used by the administration boundary."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from ..identity.errors import IdentityError
from .runtime import _PostgresAdapter, _as_utc, _jsonb


def _utc_z(value: datetime) -> str:
    return _as_utc(value).isoformat().replace("+00:00", "Z")


def _payload(record: dict[str, Any]) -> dict[str, object]:
    return {
        "request_id": str(record["request_id"]),
        "status": record["status"],
        "full_name": record["full_name"],
        "email": record["email"],
        "department": record["department"],
        "reason": record["reason"],
        "created_at": record["created_at"],
        "reviewed_at": record.get("reviewed_at"),
        "reviewed_by": record.get("reviewed_by"),
        "access_granted": False,
    }


class PostgresAccessRequestStore(_PostgresAdapter):
    """Postgres repository; failures are surfaced instead of falling back silently."""

    def create(
        self,
        *,
        tenant_id: str,
        requester_id: str,
        full_name: str,
        email: str,
        department: str,
        reason: str,
        consent: bool,
        idempotency_key: str,
        fingerprint: str,
    ) -> dict[str, object]:
        response = {
            "request_id": str(uuid4()),
            "status": "PENDING_ADMIN_REVIEW",
            "email_confirmation": "NOT_CONFIGURED",
        }
        now = datetime.now(timezone.utc)
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_uuid = self.ensure_tenant(cursor, tenant_id)
                cursor.execute(
                    """
                    SELECT request_fingerprint, safe_response
                    FROM idempotency_keys
                    WHERE tenant_id = %s AND operation = 'identity:access_request'
                      AND resource_key = 'access_request' AND idempotency_key = %s
                      AND expires_at > now()
                    """,
                    (tenant_uuid, idempotency_key),
                )
                existing = cursor.fetchone()
                if existing is not None:
                    if existing["request_fingerprint"] != fingerprint:
                        raise IdentityError(
                            "IDEMPOTENCY_KEY_REUSED",
                            409,
                            "The idempotency key was already used for a different request.",
                        )
                    stored = existing["safe_response"]
                    if isinstance(stored, dict):
                        return dict(stored)
                    raise IdentityError("DATABASE_UNAVAILABLE", 503, "The data service is temporarily unavailable.", retryable=True)

                request_id = UUID(response["request_id"])
                cursor.execute(
                    """
                    INSERT INTO access_requests
                        (id, tenant_id, requester_id, full_name, email, department, reason, consent, status, created_at)
                    VALUES (%s, %s, %s, %s, lower(btrim(%s)), %s, %s, %s, 'PENDING_ADMIN_REVIEW', %s)
                    """,
                    (request_id, tenant_uuid, requester_id, full_name, email, department, reason, consent, now),
                )
                cursor.execute(
                    """
                    INSERT INTO idempotency_keys
                        (id, tenant_id, operation, resource_key, idempotency_key,
                         request_fingerprint, response_status, safe_response, expires_at)
                    VALUES (%s, %s, 'identity:access_request', 'access_request', %s,
                            %s, 202, %s, now() + interval '1 day')
                    """,
                    (uuid4(), tenant_uuid, idempotency_key, fingerprint, _jsonb(response)),
                )
        return response

    def list(
        self,
        *,
        tenant_id: str,
        status: str,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_uuid = self.ensure_tenant(cursor, tenant_id)
                status_clause = "" if status == "ALL" else " AND status = %s"
                params: tuple[object, ...] = (tenant_uuid, *(() if status == "ALL" else (status,)))
                cursor.execute(
                    f"SELECT count(*) AS total FROM access_requests WHERE tenant_id = %s{status_clause}",
                    params,
                )
                total = int(cursor.fetchone()["total"])
                cursor.execute(
                    f"""
                    SELECT id, full_name, email, department, reason, status,
                           created_at, reviewed_at, reviewed_by
                    FROM access_requests
                    WHERE tenant_id = %s{status_clause}
                    ORDER BY created_at, id
                    LIMIT %s OFFSET %s
                    """,
                    (*params, limit, offset),
                )
                records = [
                    {
                        "request_id": row["id"],
                        "full_name": row["full_name"],
                        "email": row["email"],
                        "department": row["department"],
                        "reason": row["reason"],
                        "status": row["status"],
                        "created_at": _utc_z(row["created_at"]),
                        "reviewed_at": _utc_z(row["reviewed_at"]) if row["reviewed_at"] else None,
                        "reviewed_by": row["reviewed_by"],
                    }
                    for row in cursor.fetchall()
                ]
                return records, total

    def review(
        self,
        *,
        tenant_id: str,
        request_id: str,
        reviewer_id: str,
        decision: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> dict[str, object]:
        target_status = "APPROVED_PENDING_PROVISIONING" if decision == "APPROVE" else "REJECTED"
        with self.connection() as connection:
            with connection.cursor() as cursor:
                tenant_uuid = self.ensure_tenant(cursor, tenant_id)
                cursor.execute(
                    """
                    SELECT request_fingerprint, safe_response
                    FROM idempotency_keys
                    WHERE tenant_id = %s AND operation = 'identity:access_request_review'
                      AND resource_key = %s AND idempotency_key = %s
                      AND expires_at > now()
                    """,
                    (tenant_uuid, request_id, idempotency_key),
                )
                existing = cursor.fetchone()
                if existing is not None:
                    if existing["request_fingerprint"] != fingerprint:
                        raise IdentityError("IDEMPOTENCY_KEY_REUSED", 409, "The idempotency key was already used.")
                    stored = existing["safe_response"]
                    if isinstance(stored, dict):
                        return dict(stored)
                    raise IdentityError("DATABASE_UNAVAILABLE", 503, "The data service is temporarily unavailable.", retryable=True)

                cursor.execute(
                    """
                    SELECT id, full_name, email, department, reason, status,
                           created_at, reviewed_at, reviewed_by
                    FROM access_requests
                    WHERE id = %s AND tenant_id = %s
                    FOR UPDATE
                    """,
                    (UUID(request_id), tenant_uuid),
                )
                row = cursor.fetchone()
                if row is None:
                    raise IdentityError("NOT_FOUND_OR_FORBIDDEN", 404, "The requested resource is unavailable.")
                if row["status"] != "PENDING_ADMIN_REVIEW" and row["status"] != target_status:
                    raise IdentityError("REQUEST_CONFLICT", 409, "The access request has already been reviewed.")
                if row["status"] == "PENDING_ADMIN_REVIEW":
                    cursor.execute(
                        """
                        UPDATE access_requests
                        SET status = %s, reviewed_at = now(), reviewed_by = %s, updated_at = now()
                        WHERE id = %s AND tenant_id = %s
                        """,
                        (target_status, reviewer_id, UUID(request_id), tenant_uuid),
                    )
                    row["status"] = target_status
                    row["reviewed_at"] = datetime.now(timezone.utc)
                    row["reviewed_by"] = reviewer_id
                payload = _payload(
                    {
                        "request_id": row["id"],
                        "full_name": row["full_name"],
                        "email": row["email"],
                        "department": row["department"],
                        "reason": row["reason"],
                        "status": row["status"],
                        "created_at": _utc_z(row["created_at"]),
                        "reviewed_at": _utc_z(row["reviewed_at"]) if row["reviewed_at"] else None,
                        "reviewed_by": row["reviewed_by"],
                    }
                )
                cursor.execute(
                    """
                    INSERT INTO idempotency_keys
                        (id, tenant_id, operation, resource_key, idempotency_key,
                         request_fingerprint, response_status, safe_response, expires_at)
                    VALUES (%s, %s, 'identity:access_request_review', %s, %s,
                            %s, 200, %s, now() + interval '1 day')
                    """,
                    (uuid4(), tenant_uuid, request_id, idempotency_key, fingerprint, _jsonb(payload)),
                )
                return payload
