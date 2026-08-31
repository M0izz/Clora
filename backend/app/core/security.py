from typing import Annotated

from fastapi import Header, HTTPException, status

from backend.app.core.config import settings


async def get_current_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    x_user_role: Annotated[str | None, Header(alias="X-User-Role")] = None,
) -> dict[str, str]:
    """
    Resolve user context from request headers.
    Defaults to standard engineer role if not specified in development mode.
    """
    user_id = x_user_id.strip() if x_user_id and x_user_id.strip() else "user_default"
    role = x_user_role.strip().lower() if x_user_role and x_user_role.strip() else "engineer"

    valid_roles = {"admin", "engineer", "viewer"}
    if role not in valid_roles:
        role = "engineer"

    return {
        "id": user_id,
        "role": role,
    }


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to enforce RBAC permissions.
    """
    async def role_checker(
        current_user: Annotated[dict[str, str], get_current_user]
    ) -> dict[str, str]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {current_user['role']}",
            )
        return current_user

    return role_checker


async def validate_internal_service_key(
    x_internal_service_key: Annotated[str | None, Header(alias="X-Internal-Service-Key")] = None,
) -> bool:
    """
    Validate M2M worker service key for backend-to-worker internal status callbacks.
    """
    if not x_internal_service_key or x_internal_service_key != settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing internal service key",
        )
    return True
