import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import Workspace, File, Query
from app.services.audit_service import log_action


def get_workspace_dir(workspace_id: str) -> Path:
    """Returns the dedicated directory path for a workspace."""
    ws_dir = settings.STORAGE_DIR / "workspaces" / workspace_id
    ws_dir.mkdir(parents=True, exist_ok=True)
    return ws_dir


def create_workspace(
    db: Session,
    name: str,
    description: str | None = None,
    owner_id: str | None = None,
) -> Workspace:
    """Creates a new workspace and initializes its storage directory."""
    workspace = Workspace(
        name=name.strip(),
        description=description.strip() if description else None,
        owner_id=owner_id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Initialize physical storage directory
    get_workspace_dir(workspace.id)

    # Audit logging
    log_action(
        db=db,
        action="CREATE_WORKSPACE",
        resource="workspace",
        user_id=owner_id,
        workspace_id=workspace.id,
        details={"workspace_name": workspace.name, "description": workspace.description},
    )

    return workspace


def get_workspace(db: Session, workspace_id: str) -> dict | None:
    """Fetch a single workspace with computed counts."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return None

    files_count = db.query(File).filter(File.workspace_id == workspace.id).count()
    queries_count = db.query(Query).filter(Query.workspace_id == workspace.id).count()

    return {
        "id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "owner_id": workspace.owner_id,
        "created_at": workspace.created_at,
        "files_count": files_count,
        "queries_count": queries_count,
    }


def list_workspaces(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    """Fetch paginated workspaces with item counts."""
    total = db.query(Workspace).count()
    workspaces = db.query(Workspace).offset(skip).limit(limit).all()

    items = []
    for ws in workspaces:
        files_count = db.query(File).filter(File.workspace_id == ws.id).count()
        queries_count = db.query(Query).filter(Query.workspace_id == ws.id).count()
        items.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "owner_id": ws.owner_id,
            "created_at": ws.created_at,
            "files_count": files_count,
            "queries_count": queries_count,
        })

    return items, total


def delete_workspace(
    db: Session,
    workspace_id: str,
    user_id: str | None = None,
) -> bool:
    """Deletes a workspace, triggers cascade DB deletion, cleans up disk, and records audit."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return False

    ws_name = workspace.name

    # Snapshot audit log before deleting record
    log_action(
        db=db,
        action="DELETE_WORKSPACE",
        resource="workspace",
        user_id=user_id,
        workspace_id=workspace_id,
        details={"workspace_name": ws_name, "deleted": True},
    )

    db.delete(workspace)
    db.commit()

    # Clean up physical directory from disk
    ws_dir = settings.STORAGE_DIR / "workspaces" / workspace_id
    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)

    return True
