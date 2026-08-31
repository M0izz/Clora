from typing import Any

from sqlalchemy.orm import Session

from backend.app.db.models import AuditLog, Workspace


def log_action(
    db: Session,
    action: str,
    resource: str,
    user_id: str | None = None,
    workspace_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Record an immutable audit event with forensic snapshotting.
    Automatically captures snapshot metadata (such as workspace_name)
    so historical logs remain intelligible even after entity deletion.
    """
    snapshot_details: dict[str, Any] = dict(details) if details else {}

    # Snapshot workspace name if workspace_id is provided and name is not already snapshotted
    if workspace_id and "workspace_name" not in snapshot_details:
        ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if ws:
            snapshot_details["workspace_name"] = ws.name

    audit_entry = AuditLog(
        user_id=user_id,
        workspace_id=workspace_id,
        action=action,
        resource=resource,
        details=snapshot_details,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
