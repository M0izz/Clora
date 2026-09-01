from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import IngestionJob
from backend.app.schemas.ingestion import IngestionJobListResponse, IngestionJobResponse

router = APIRouter(tags=["Ingestion"])


@router.get(
    "/ingestion/{job_id}",
    response_model=IngestionJobResponse,
    summary="Poll Document Ingestion Status",
)
def get_ingestion_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Poll status of in-process document ingestion.
    Possible states: QUEUED, PROCESSING, INDEXING, COMPLETED, FAILED.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion job '{job_id}' not found",
        )
    return job


@router.get(
    "/ingestion/workspace/{workspace_id}",
    response_model=IngestionJobListResponse,
    summary="List Ingestion Jobs for Workspace",
)
def list_workspace_ingestion_jobs(
    workspace_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve all document processing jobs within a workspace.
    """
    jobs = (
        db.query(IngestionJob)
        .filter(IngestionJob.workspace_id == workspace_id)
        .order_by(IngestionJob.created_at.desc())
        .all()
    )
    return {
        "jobs": jobs,
        "total": len(jobs),
    }
