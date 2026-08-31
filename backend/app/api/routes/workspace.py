from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.database import get_db
from backend.app.schemas.common import MessageResponse
from backend.app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceResponse,
)
from backend.app.services import workspace_service

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED, summary="Create Workspace")
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new industrial intelligence workspace (e.g. 'Refinery Unit 4')
    and provision its dedicated storage repository.
    """
    ws = workspace_service.create_workspace(
        db=db,
        name=data.name,
        description=data.description,
        owner_id=current_user.get("id"),
    )
    return {
        "id": ws.id,
        "name": ws.name,
        "description": ws.description,
        "owner_id": ws.owner_id,
        "created_at": ws.created_at,
        "files_count": 0,
        "queries_count": 0,
    }


@router.get("", response_model=WorkspaceListResponse, summary="List Workspaces")
def list_workspaces(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Page size limit"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all workspaces with associated document and query counts.
    """
    items, total = workspace_service.list_workspaces(db=db, skip=skip, limit=limit)
    return {
        "items": items,
        "total": total,
    }


@router.get("/{workspace_id}", response_model=WorkspaceResponse, summary="Get Workspace Details")
def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch single workspace details and status.
    """
    ws_data = workspace_service.get_workspace(db=db, workspace_id=workspace_id)
    if not ws_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )
    return ws_data


@router.delete("/{workspace_id}", response_model=MessageResponse, summary="Delete Workspace")
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cascade delete a workspace, its associated database records, and disk files.
    """
    success = workspace_service.delete_workspace(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.get("id"),
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )
    return {
        "message": f"Workspace '{workspace_id}' successfully deleted",
        "success": True,
    }
