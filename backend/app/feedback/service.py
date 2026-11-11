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


class FeedbackRepository(Protocol):
    def find(self, *, answer_id: str, actor_id: str) -> tuple[str, FeedbackRecord] | None: ...

    def save(self, *, answer_id: str, actor_id: str, fingerprint: str, record: FeedbackRecord) -> None: ...

    def find_idempotency(self, *, actor_id: str, key: str) -> tuple[str, FeedbackRecord] | None: ...

    def save_idempotency(self, *, actor_id: str, key: str, fingerprint: str, record: FeedbackRecord) -> None: ...


class InMemoryFeedbackRepository:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], tuple[str, FeedbackRecord]] = {}
        self._idempotency: dict[tuple[str, str], tuple[str, FeedbackRecord]] = {}
        self._lock = RLock()

    def find(self, *, answer_id: str, actor_id: str) -> tuple[str, FeedbackRecord] | None:
        with self._lock:
            return self._records.get((answer_id, actor_id))

    def save(self, *, answer_id: str, actor_id: str, fingerprint: str, record: FeedbackRecord) -> None:
        with self._lock:
            self._records[(answer_id, actor_id)] = (fingerprint, record)

    def find_idempotency(self, *, actor_id: str, key: str) -> tuple[str, FeedbackRecord] | None:
        with self._lock:
            return self._idempotency.get((actor_id, key))

    def save_idempotency(self, *, actor_id: str, key: str, fingerprint: str, record: FeedbackRecord) -> None:
        with self._lock:
            self._idempotency[(actor_id, key)] = (fingerprint, record)


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
    ) -> tuple[FeedbackRecord, bool]:
        if not idempotency_key or len(idempotency_key.strip()) < 16:
            raise IdentityError("IDEMPOTENCY_REQUIRED", 400, "An idempotency key is required.")
        rating = rating.strip().upper()
        if rating not in {"POSITIVE", "NEGATIVE"} or (comment is not None and len(comment) > 4_000):
            raise IdentityError("REQUEST_INVALID", 400, "The request is invalid.")
        key = idempotency_key.strip()
        fingerprint = f"{rating}:{comment or ''}"
        replay = self.repository.find_idempotency(actor_id=actor_id, key=key)
        if replay is not None:
            if replay[0] != fingerprint:
                raise IdentityError("IDEMPOTENCY_KEY_REUSED", 409, "The idempotency key was already used.")
            return replay[1], True
        existing = self.repository.find(answer_id=answer_id, actor_id=actor_id)
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
        )
        self.repository.save(answer_id=answer_id, actor_id=actor_id, fingerprint=fingerprint, record=record)
        self.repository.save_idempotency(actor_id=actor_id, key=key, fingerprint=fingerprint, record=record)
        return record, False


__all__ = ["FeedbackRecord", "FeedbackRepository", "FeedbackService", "InMemoryFeedbackRepository"]
