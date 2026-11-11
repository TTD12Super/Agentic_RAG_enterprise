"""Idempotent, privacy-safe chat feedback boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Protocol
from uuid import uuid4

from ..identity.errors import IdentityError


@dataclass(frozen=True, slots=True)
class FeedbackRecord:
    feedback_id: str
    answer_id: str
    actor_id: str
    rating: str
    comment: str | None
    created_at: datetime
    tenant_id: str = "public"


@dataclass(frozen=True, slots=True)
class FeedbackReview:
    """Admin review projection; body, comment and actor identity stay internal."""

    feedback_id: str
    answer_id: str
    rating: str
    created_at: datetime


class FeedbackRepository(Protocol):
    def find(
        self, *, answer_id: str, actor_id: str, tenant_id: str = "public"
    ) -> tuple[str, FeedbackRecord] | None: ...

    def list_records(self, *, tenant_id: str) -> tuple[FeedbackRecord, ...]: ...

    def save(self, *, answer_id: str, actor_id: str, fingerprint: str, record: FeedbackRecord) -> None: ...

    def find_idempotency(
        self, *, actor_id: str, key: str, tenant_id: str = "public"
    ) -> tuple[str, FeedbackRecord] | None: ...

    def save_idempotency(self, *, actor_id: str, key: str, fingerprint: str, record: FeedbackRecord) -> None: ...


class InMemoryFeedbackRepository:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], tuple[str, FeedbackRecord]] = {}
        self._idempotency: dict[tuple[str, str, str], tuple[str, FeedbackRecord]] = {}
        self._lock = RLock()

    def find(self, *, answer_id: str, actor_id: str, tenant_id: str = "public") -> tuple[str, FeedbackRecord] | None:
        with self._lock:
            return self._records.get((tenant_id, answer_id, actor_id))

    def list_records(self, *, tenant_id: str) -> tuple[FeedbackRecord, ...]:
        with self._lock:
            return tuple(
                sorted(
                    (record for (record_tenant, _, _), (_, record) in self._records.items() if record_tenant == tenant_id),
                    key=lambda record: (record.created_at, record.feedback_id),
                    reverse=True,
                )
            )

    def save(self, *, answer_id: str, actor_id: str, fingerprint: str, record: FeedbackRecord) -> None:
        with self._lock:
            self._records[(record.tenant_id, answer_id, actor_id)] = (fingerprint, record)

    def find_idempotency(self, *, actor_id: str, key: str, tenant_id: str = "public") -> tuple[str, FeedbackRecord] | None:
        with self._lock:
            return self._idempotency.get((tenant_id, actor_id, key))

    def save_idempotency(self, *, actor_id: str, key: str, fingerprint: str, record: FeedbackRecord) -> None:
        with self._lock:
            self._idempotency[(record.tenant_id, actor_id, key)] = (fingerprint, record)


class FeedbackService:
    def __init__(self, repository: FeedbackRepository | None = None) -> None:
        self.repository = repository or InMemoryFeedbackRepository()

    def submit(
        self,
        *,
        answer_id: str,
        actor_id: str,
        rating: str,
        comment: str | None,
        idempotency_key: str | None,
        tenant_id: str = "public",
    ) -> tuple[FeedbackRecord, bool]:
        if not idempotency_key or len(idempotency_key.strip()) < 16:
            raise IdentityError("IDEMPOTENCY_REQUIRED", 400, "An idempotency key is required.")
        rating = rating.strip().upper()
        if rating not in {"POSITIVE", "NEGATIVE"} or (comment is not None and len(comment) > 4_000):
            raise IdentityError("REQUEST_INVALID", 400, "The request is invalid.")
        key = idempotency_key.strip()
        fingerprint = f"{rating}:{comment or ''}"
        replay = self.repository.find_idempotency(actor_id=actor_id, key=key, tenant_id=tenant_id)
        if replay is not None:
            if replay[0] != fingerprint:
                raise IdentityError("IDEMPOTENCY_KEY_REUSED", 409, "The idempotency key was already used.")
            return replay[1], True
        existing = self.repository.find(answer_id=answer_id, actor_id=actor_id, tenant_id=tenant_id)
        if existing is not None:
            if existing[0] != fingerprint:
                raise IdentityError("FEEDBACK_ALREADY_RECORDED", 409, "Feedback was already recorded.")
            self.repository.save_idempotency(
                actor_id=actor_id, key=key, fingerprint=fingerprint, record=existing[1]
            )
            return existing[1], True
        record = FeedbackRecord(
            feedback_id=f"feedback-{uuid4()}",
            answer_id=answer_id,
            actor_id=actor_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(timezone.utc),
            tenant_id=tenant_id,
        )
        self.repository.save(answer_id=answer_id, actor_id=actor_id, fingerprint=fingerprint, record=record)
        self.repository.save_idempotency(actor_id=actor_id, key=key, fingerprint=fingerprint, record=record)
        return record, False

    def review(
        self,
        *,
        tenant_id: str,
        limit: int,
        offset: int,
        rating: str | None = None,
    ) -> tuple[tuple[FeedbackReview, ...], int]:
        records = self.repository.list_records(tenant_id=tenant_id)
        if rating is not None:
            records = tuple(record for record in records if record.rating == rating)
        total = len(records)
        return (
            tuple(
                FeedbackReview(
                    feedback_id=record.feedback_id,
                    answer_id=record.answer_id,
                    rating=record.rating,
                    created_at=record.created_at,
                )
                for record in records[offset : offset + limit]
            ),
            total,
        )


__all__ = [
    "FeedbackRecord",
    "FeedbackRepository",
    "FeedbackReview",
    "FeedbackService",
    "InMemoryFeedbackRepository",
]
