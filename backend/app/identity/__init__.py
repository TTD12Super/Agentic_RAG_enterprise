"""Provider-neutral identity and session boundary."""

from .models import AuthenticatedPrincipal, Role
from .service import AuthenticationService
from .store import InMemoryIdentityStore

__all__ = [
    "AuthenticatedPrincipal",
    "AuthenticationService",
    "InMemoryIdentityStore",
    "Role",
]
