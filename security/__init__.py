"""
Security & Audit Package for INDUSAI-X (SIH PS 26117).
Contains RBAC permission enforcement, thread-safe SHA-256 audit logging, and air-gap network verification.
"""

from .rbac import (
    ROLE_PERMISSIONS,
    check_permission,
    enforce_permission,
    PermissionDeniedError
)

from .audit_trail import (
    AuditLogger,
    GENESIS_HASH
)

from .airgap_monitor import (
    check_network_isolation,
    is_local_address
)

__all__ = [
    "ROLE_PERMISSIONS",
    "check_permission",
    "enforce_permission",
    "PermissionDeniedError",
    "AuditLogger",
    "GENESIS_HASH",
    "check_network_isolation",
    "is_local_address"
]
