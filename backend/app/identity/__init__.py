"""Provider-neutral identity and session boundary."""

from .models import AuthenticatedPrincipal, DepartmentRecord, Role
from .service import AuthenticationService
from .store import InMemoryIdentityStore

__all__ = [
    "AuthenticatedPrincipal",
    "DepartmentRecord",
    "AuthenticationService",
    "InMemoryIdentityStore",
    "Role",
]
