"""
Role-Based Access Control (RBAC) Module for INDUSAI-X.
SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Implements the concrete 5-role permission matrix:
Roles: Admin, Plant_Engineer, Safety_Officer, Auditor, Operator.
"""

from typing import Dict, Set


class PermissionDeniedError(Exception):
    """Raised when a user role lacks permission for a requested action."""
    pass


# Concrete RBAC Matrix
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "Admin": {
        "read_document",
        "run_ocr",
        "query_tabular",
        "generate_approval_note",
        "export_report",
        "view_audit_log",
        "verify_audit_log"
    },
    "Plant_Engineer": {
        "read_document",
        "run_ocr",
        "query_tabular",
        "generate_approval_note",
        "export_report"
    },
    "Safety_Officer": {
        "read_document",
        "run_ocr",
        "query_tabular",
        "export_report"
    },
    "Auditor": {
        "read_document",
        "query_tabular",
        "export_report",
        "view_audit_log",
        "verify_audit_log"
    },
    "Operator": {
        "read_document"
    }
}

# Default roles allowed to read ingested documents (used as ChromaDB metadata)
DEFAULT_DOCUMENT_ROLES = "Admin,Plant_Engineer,Safety_Officer,Auditor"


class RBACEnforcer:
    """Class-based RBAC enforcer for use by integration_bridge.py."""

    def require(self, role: str, action: str) -> None:
        """Raises PermissionError if role is not authorized for action."""
        enforce_permission(role, action)

    def is_allowed(self, role: str, action: str) -> bool:
        """Returns True if role can perform action."""
        return check_permission(role, action)


def check_permission(role: str, action: str) -> bool:
    """Checks whether a given role is authorized to perform an action."""
    permissions = ROLE_PERMISSIONS.get(role, set())
    return action in permissions


def enforce_permission(role: str, action: str) -> None:
    """
    Enforces role authorization.
    Raises PermissionDeniedError if the role is unauthorized.
    """
    if not check_permission(role, action):
        valid_roles = [r for r, p in ROLE_PERMISSIONS.items() if action in p]
        raise PermissionDeniedError(
            f"Access Denied: Role '{role}' is not authorized to perform action '{action}'. "
            f"Required roles: {valid_roles}"
        )
