from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import AuditLog, Workspace
from app.schemas.audit import AuditLogListResponse, AuditLogResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


def resolve_workspace_label(db: Session, audit_entry: AuditLog) -> str | None:
    """
    Forensic Snapshot Resolution:
    If workspace currently exists, returns its active name.
    If workspace has been deleted, recovers the snapshot name from audit details
    and appends '(deleted)' so logs remain permanently intelligible.
    """
    if not audit_entry.workspace_id:
        return None

    ws = db.query(Workspace).filter(Workspace.id == audit_entry.workspace_id).first()
    if ws:
        return ws.name

    # Graceful recovery from recorded snapshot details
    details = audit_entry.details or {}
    snapshot_name = details.get("workspace_name")
    if snapshot_name:
        return f"{snapshot_name} (deleted)"

    return f"{audit_entry.workspace_id} (deleted)"


@router.get("", response_model=AuditLogListResponse, summary="Query Audit Logs")
def list_audit_logs(
    workspace_id: str | None = Query(None, description="Filter by workspace ID"),
    action: str | None = Query(None, description="Filter by action name"),
    user_id: str | None = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve forensic audit logs with search filters and immutable snapshot resolution.
    """
    query = db.query(AuditLog)

    if workspace_id:
        query = query.filter(AuditLog.workspace_id == workspace_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    total = query.count()
    records = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "user_id": r.user_id,
            "workspace_id": r.workspace_id,
            "workspace_label": resolve_workspace_label(db, r),
            "action": r.action,
            "resource": r.resource,
            "details": r.details,
            "timestamp": r.timestamp,
        })

    return {
        "items": items,
        "total": total,
    }


@router.get("/{audit_id}", response_model=AuditLogResponse, summary="Get Audit Entry Details")
def get_audit_log(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a single detailed audit log record.
    """
    r = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit record '{audit_id}' not found",
        )

    return {
        "id": r.id,
        "user_id": r.user_id,
        "workspace_id": r.workspace_id,
        "workspace_label": resolve_workspace_label(db, r),
        "action": r.action,
        "resource": r.resource,
        "details": r.details,
        "timestamp": r.timestamp,
    }
