"""Small, fail-closed PDP and PEP for the v1 authorization contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Callable, Iterable, Protocol

from ..identity.models import AuthenticatedPrincipal, CANONICAL_ROLES


class Decision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class Action(StrEnum):
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPDATE = "document:update"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_APPROVE = "document:approve"
    DOCUMENT_PUBLISH = "document:publish"
    SOURCE_DOWNLOAD = "source:download"
    TOOL_EXECUTE = "tool:execute"
    CONVERSATION_READ = "conversation:read"
    FEEDBACK_CREATE = "feedback:create"


ACTIONS = frozenset(action.value for action in Action)
READ_ACTIONS = frozenset({Action.DOCUMENT_READ.value, Action.SOURCE_DOWNLOAD.value})
_ACTION_ALIASES = {
    "DOCUMENT_CREATE": Action.DOCUMENT_CREATE.value,
    "DOCUMENT_READ": Action.DOCUMENT_READ.value,
    "DOCUMENT_UPDATE": Action.DOCUMENT_UPDATE.value,
    "DOCUMENT_DELETE": Action.DOCUMENT_DELETE.value,
    "DOCUMENT_APPROVE": Action.DOCUMENT_APPROVE.value,
    "DOCUMENT_PUBLISH": Action.DOCUMENT_PUBLISH.value,
    "SOURCE_DOWNLOAD": Action.SOURCE_DOWNLOAD.value,
    "TOOL_EXECUTE": Action.TOOL_EXECUTE.value,
    "CONVERSATION_READ": Action.CONVERSATION_READ.value,
    "FEEDBACK_CREATE": Action.FEEDBACK_CREATE.value,
}


class Classification(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"


class Effect(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class AnonymousPrincipal:
    """Server-resolved anonymous identity; it has no roles or user identity."""

    tenant_id: str
    session_id: str | None = None


@dataclass(frozen=True)
class AccessGrant:
    """A document or tenant grant matching one principal attribute."""

    action: str
    effect: str
    tenant_id: str | None = None
    user_id: str | None = None
    role: str | None = None
    group: str | None = None
    department_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", _normalize_action(self.action))
        object.__setattr__(
            self,
            "effect",
            self.effect.value if isinstance(self.effect, Effect) else str(self.effect).upper(),
        )
        if self.action != "*" and self.action not in ACTIONS:
            raise ValueError("grant action must be canonical")
        if self.effect not in {Effect.ALLOW.value, Effect.DENY.value}:
            raise ValueError("grant effect must be ALLOW or DENY")
        if self.role is not None and self.role not in CANONICAL_ROLES:
            raise ValueError("grant role must be canonical")
        if sum(value is not None for value in (self.user_id, self.role, self.group, self.department_id)) > 1:
            raise ValueError("a grant may target only one principal attribute")

    def matches(
        self,
        principal: AuthenticatedPrincipal | AnonymousPrincipal | None,
        action: str,
        tenant_id: str,
    ) -> bool:
        if self.tenant_id is not None and self.tenant_id != tenant_id:
            return False
        if self.action not in {"*", action}:
            return False
        if self.user_id is None and self.role is None and self.group is None and self.department_id is None:
            return True
        if principal is None or isinstance(principal, AnonymousPrincipal):
            return False
        return any(
            (
                self.user_id is not None and self.user_id == principal.user_id,
                self.role is not None and self.role in principal.roles,
                self.group is not None and self.group in principal.groups,
                self.department_id is not None and self.department_id in principal.department_ids,
            )
        )


@dataclass(frozen=True)
class DocumentResource:
    """Authoritative document/version metadata passed to the PDP."""

    document_id: str
    tenant_id: str
    classification: str
    status: str = "ACTIVE"
    current_version_id: str | None = None
    version_id: str | None = None
    version_status: str = "ACTIVE"
    owner_department_id: str | None = None
    owner_user_id: str | None = None
    acl: tuple[AccessGrant, ...] = field(default_factory=tuple)
    policy_epoch: int | None = None
    revoked_at: datetime | None = None


@dataclass(frozen=True)
class ConversationResource:
    """Conversation metadata used for owner-only body access."""

    conversation_id: str
    tenant_id: str
    owner_user_id: str
    status: str = "ACTIVE"
    policy_epoch: int | None = None


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    principal_id: str | None
    resource_type: str
    resource_id: str | None
    action: str
    policy_epoch: int | None
    reason_code: str
    evaluated_at: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


class PolicyStore(Protocol):
    def current_policy_epoch(self) -> int: ...

    def tenant_grants(self, tenant_id: str) -> Iterable[AccessGrant]: ...

    def principal_revoked(self, principal_id: str, tenant_id: str) -> bool: ...


@dataclass
class InMemoryPolicyStore:
    """Deterministic adapter for tests and the initial service boundary."""

    policy_epoch: int
    grants: dict[str, tuple[AccessGrant, ...]] = field(default_factory=dict)
    revoked_principals: set[tuple[str, str]] = field(default_factory=set)
    available: bool = True

    def current_policy_epoch(self) -> int:
        if not self.available:
            raise RuntimeError("policy store unavailable")
        return self.policy_epoch

    def tenant_grants(self, tenant_id: str) -> Iterable[AccessGrant]:
        if not self.available:
            raise RuntimeError("policy store unavailable")
        return self.grants.get(tenant_id, ())

    def principal_revoked(self, principal_id: str, tenant_id: str) -> bool:
        if not self.available:
            raise RuntimeError("policy store unavailable")
        return (tenant_id, principal_id) in self.revoked_principals


class AuthorizationEvaluator:
    """Trusted PDP. Every unknown, stale or unavailable input returns DENY."""

    _ROLE_ACTIONS = {
        "system_admin": ACTIONS - {Action.CONVERSATION_READ.value},
        "website_manager": {
            Action.DOCUMENT_CREATE.value,
            Action.DOCUMENT_READ.value,
            Action.DOCUMENT_UPDATE.value,
            Action.DOCUMENT_DELETE.value,
            Action.DOCUMENT_APPROVE.value,
            Action.DOCUMENT_PUBLISH.value,
            Action.SOURCE_DOWNLOAD.value,
            Action.FEEDBACK_CREATE.value,
        },
        "employee": {
            Action.DOCUMENT_READ.value,
            Action.SOURCE_DOWNLOAD.value,
            Action.TOOL_EXECUTE.value,
            Action.CONVERSATION_READ.value,
            Action.FEEDBACK_CREATE.value,
        },
        "chairman": {
            Action.DOCUMENT_READ.value,
            Action.SOURCE_DOWNLOAD.value,
            Action.CONVERSATION_READ.value,
            Action.FEEDBACK_CREATE.value,
        },
    }

    def __init__(
        self,
        policy_store: PolicyStore | None = None,
        *,
        policy_epoch: int | None = None,
        current_policy_epoch: int | None = None,
        clock: Callable[[], datetime] | None = None,
        grants: Iterable[AccessGrant] = (),
    ) -> None:
        if policy_epoch is not None and current_policy_epoch is not None and policy_epoch != current_policy_epoch:
            raise ValueError("policy_epoch and current_policy_epoch disagree")
        self.policy_store = policy_store
        self.policy_epoch = policy_epoch if policy_epoch is not None else current_policy_epoch
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.grants = tuple(grants)

    def evaluate(
        self,
        principal: AuthenticatedPrincipal | AnonymousPrincipal | None,
        action: str,
        resource: DocumentResource | ConversationResource | None = None,
        *,
        tenant_id: str | None = None,
        policy_epoch: int | None = None,
        current_policy_epoch: int | None = None,
    ) -> PolicyDecision:
        normalized_action = _normalize_action(action)
        resource_type = (
            "document"
            if isinstance(resource, DocumentResource)
            else "conversation"
            if isinstance(resource, ConversationResource)
            else _resource_type(normalized_action)
        )
        resource_id = getattr(resource, "document_id", None) or getattr(resource, "conversation_id", None)
        principal_id = getattr(principal, "user_id", None)
        evaluated_at = self.clock().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        def deny(reason: str, epoch: int | None = None) -> PolicyDecision:
            return PolicyDecision(
                decision=Decision.DENY,
                principal_id=principal_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=normalized_action,
                policy_epoch=epoch,
                reason_code=reason,
                evaluated_at=evaluated_at,
            )

        if normalized_action not in ACTIONS:
            return deny("UNKNOWN_ACTION")

        try:
            current_epoch = self._read_current_epoch()
            requested_epoch = (
                policy_epoch
                if policy_epoch is not None
                else current_policy_epoch
                if current_policy_epoch is not None
                else current_epoch
            )
            if not _valid_epoch(current_epoch) or not _valid_epoch(requested_epoch):
                return deny("POLICY_STALE", current_epoch)
            if requested_epoch != current_epoch:
                return deny("POLICY_STALE", current_epoch)
        except Exception:
            return deny("POLICY_UNAVAILABLE")

        if principal is not None and not self._valid_principal(principal):
            return deny("INVALID_PRINCIPAL", current_epoch)
        principal_tenant = getattr(principal, "tenant_id", None)
        if principal_tenant is None:
            principal_tenant = tenant_id or getattr(resource, "tenant_id", None)
        if not principal_tenant or (tenant_id is not None and tenant_id != principal_tenant):
            return deny("TENANT_MISMATCH", current_epoch)
        if resource is not None:
            if not isinstance(resource, (DocumentResource, ConversationResource)):
                return deny("INVALID_RESOURCE", current_epoch)
            if resource.tenant_id != principal_tenant:
                return deny("TENANT_MISMATCH", current_epoch)
            if resource.policy_epoch is not None and resource.policy_epoch != current_epoch:
                return deny("POLICY_STALE", current_epoch)

        try:
            if isinstance(principal, AuthenticatedPrincipal) and self._principal_revoked(principal):
                return deny("PRINCIPAL_REVOKED", current_epoch)
        except Exception:
            return deny("POLICY_UNAVAILABLE", current_epoch)

        if resource is not None and isinstance(resource, DocumentResource):
            if resource.classification not in {value.value for value in Classification}:
                return deny("UNKNOWN_CLASSIFICATION", current_epoch)
            if resource.revoked_at is not None or resource.status != "ACTIVE":
                return deny("RESOURCE_REVOKED", current_epoch)
            if normalized_action in READ_ACTIONS and (
                not resource.current_version_id
                or resource.version_id != resource.current_version_id
                or resource.version_status != "ACTIVE"
            ):
                return deny("VERSION_NOT_CURRENT", current_epoch)
        elif resource is not None and isinstance(resource, ConversationResource):
            if resource.status != "ACTIVE":
                return deny("RESOURCE_REVOKED", current_epoch)
        elif normalized_action in READ_ACTIONS or normalized_action.startswith("document:"):
            if normalized_action in READ_ACTIONS or normalized_action != Action.DOCUMENT_CREATE.value:
                return deny("RESOURCE_REQUIRED", current_epoch)

        if normalized_action in READ_ACTIONS and not isinstance(resource, DocumentResource):
            return deny("INVALID_RESOURCE", current_epoch)
        if resource is not None and normalized_action.startswith("document:") and not isinstance(resource, DocumentResource):
            return deny("INVALID_RESOURCE", current_epoch)
        if normalized_action == Action.CONVERSATION_READ.value and not isinstance(resource, ConversationResource):
            return deny("RESOURCE_REQUIRED", current_epoch)

        try:
            grants = list(self.grants)
            if self.policy_store is not None:
                grants.extend(self.policy_store.tenant_grants(principal_tenant))
            if isinstance(resource, DocumentResource):
                grants.extend(resource.acl)
        except Exception:
            return deny("POLICY_UNAVAILABLE", current_epoch)

        matching = [grant for grant in grants if grant.matches(principal, normalized_action, principal_tenant)]
        if any(grant.effect == Effect.DENY.value for grant in matching):
            return deny("EXPLICIT_DENY", current_epoch)

        if normalized_action == Action.CONVERSATION_READ.value:
            if resource.owner_user_id != principal_id:  # type: ignore[union-attr]
                return deny("OWNER_ONLY", current_epoch)

        role_allowed = self._role_allows(principal, normalized_action)
        if not role_allowed:
            return deny(
                "CHAIRMAN_READ_ONLY" if self._has_role(principal, "chairman") else "ROLE_DENY",
                current_epoch,
            )

        if resource is not None and normalized_action in READ_ACTIONS:
            if isinstance(principal, AnonymousPrincipal) or principal is None:
                if resource.classification != Classification.PUBLIC.value:
                    return deny("ANONYMOUS_PUBLIC_ONLY", current_epoch)
            elif "employee" in principal.roles and resource.classification == Classification.INTERNAL.value:
                assigned = resource.owner_department_id in principal.department_ids
                assigned = assigned or any(grant.effect == Effect.ALLOW.value for grant in matching)
                if not assigned:
                    return deny("DEPARTMENT_DENY", current_epoch)

        reason = "ACL_ALLOW" if any(grant.effect == Effect.ALLOW.value for grant in matching) else "RBAC_ALLOW"
        if isinstance(resource, DocumentResource) and resource.classification == Classification.PUBLIC.value and normalized_action in READ_ACTIONS:
            reason = "PUBLIC_ALLOW"
        return PolicyDecision(
            decision=Decision.ALLOW,
            principal_id=principal_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=normalized_action,
            policy_epoch=current_epoch,
            reason_code=reason,
            evaluated_at=evaluated_at,
        )

    def _read_current_epoch(self) -> int | None:
        if self.policy_store is not None:
            return self.policy_store.current_policy_epoch()
        return self.policy_epoch

    def _principal_revoked(self, principal: AuthenticatedPrincipal) -> bool:
        if self.policy_store is None:
            return False
        return self.policy_store.principal_revoked(principal.user_id, principal.tenant_id)

    @staticmethod
    def _valid_principal(principal: object) -> bool:
        if isinstance(principal, AnonymousPrincipal):
            return bool(principal.tenant_id)
        if not isinstance(principal, AuthenticatedPrincipal):
            return False
        return bool(
            principal.user_id
            and principal.tenant_id
            and principal.session_id
            and principal.auth_time
            and principal.roles
            and len(principal.roles) == len(set(principal.roles))
            and set(principal.roles) <= CANONICAL_ROLES
        )

    def _role_allows(
        self,
        principal: AuthenticatedPrincipal | AnonymousPrincipal | None,
        action: str,
    ) -> bool:
        if principal is None or isinstance(principal, AnonymousPrincipal):
            return action in READ_ACTIONS
        return any(action in self._ROLE_ACTIONS.get(role, set()) for role in principal.roles)

    @staticmethod
    def _has_role(principal: object, role: str) -> bool:
        return isinstance(principal, AuthenticatedPrincipal) and role in principal.roles


class AuthorizationDenied(PermissionError):
    """PEP denial with a safe, non-existence-revealing error code."""

    code = "NOT_FOUND_OR_FORBIDDEN"

    def __init__(self, decision: PolicyDecision) -> None:
        self.decision = decision
        super().__init__(self.code)


class PolicyEnforcementPoint:
    """Reusable boundary for API, retrieval, tools, citation and cache callers."""

    def __init__(self, evaluator: AuthorizationEvaluator) -> None:
        self.evaluator = evaluator

    def check(self, *args: object, **kwargs: object) -> PolicyDecision:
        return self.evaluator.evaluate(*args, **kwargs)  # type: ignore[arg-type]

    def enforce(self, *args: object, **kwargs: object) -> PolicyDecision:
        decision = self.check(*args, **kwargs)
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


def _normalize_action(action: str) -> str:
    value = action.value if isinstance(action, Action) else str(action)
    return _ACTION_ALIASES.get(value, value)


def _resource_type(action: str) -> str:
    return "document" if action.startswith("document:") or action == Action.SOURCE_DOWNLOAD.value else action.split(":", 1)[0]


def _valid_epoch(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


PDP = AuthorizationEvaluator
PEP = PolicyEnforcementPoint
