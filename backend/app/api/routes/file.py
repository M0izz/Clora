from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi import (
    File as FastAPIFile,
)
from fastapi.responses import FileResponse as FastAPIFileresponse
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user, validate_internal_service_key
from backend.app.db.database import get_db
from backend.app.schemas.common import MessageResponse
from backend.app.schemas.file import FileListResponse, FileResponse, FileStatusUpdate
from backend.app.services import file_service
from backend.app.services.ingestion_service import create_ingestion_job, process_ingestion_job

router = APIRouter(tags=["Files"])


@router.post(
    "/workspaces/{workspace_id}/files",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Industrial File",
)
async def upload_file(
    workspace_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(..., description="Industrial PDF, diagram image, or telemetry CSV"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Securely ingest industrial documents, drawings, or sensor data.
    Validates magic bytes, enforces size limits, and dispatches in-process background ingestion.
    """
    file_record = await file_service.save_uploaded_file(
        db=db,
        workspace_id=workspace_id,
        upload_file=file,
        user_id=current_user.get("id"),
    )

    # Create Ingestion Job and dispatch BackgroundTask
    job = create_ingestion_job(
        db=db,
        file_id=file_record.id,
        workspace_id=workspace_id,
        filename=file_record.filename,
    )
    background_tasks.add_task(process_ingestion_job, job.id)

    res = FileResponse.model_validate(file_record)
    res.ingestion_job_id = job.id
    return res


@router.post(
    "/files/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload File with Workspace ID Form",
)
async def upload_file_direct(
    background_tasks: BackgroundTasks,
    workspace_id: str = Form(..., description="Target Workspace UUID"),
    file: UploadFile = FastAPIFile(..., description="File to ingest"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Direct upload endpoint alias matching API_CONTRACTS.md: POST /api/files/upload.
    """
    file_record = await file_service.save_uploaded_file(
        db=db,
        workspace_id=workspace_id,
        upload_file=file,
        user_id=current_user.get("id"),
    )

    job = create_ingestion_job(
        db=db,
        file_id=file_record.id,
        workspace_id=workspace_id,
        filename=file_record.filename,
    )
    background_tasks.add_task(process_ingestion_job, job.id)

    res = FileResponse.model_validate(file_record)
    res.ingestion_job_id = job.id
    return res


@router.get(
    "/workspaces/{workspace_id}/files",
    response_model=FileListResponse,
    summary="List Files in Workspace",
)
def list_files(
    workspace_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all ingested documents and telemetry datasets in the specified workspace.
    """
    files, total = file_service.list_workspace_files(
        db=db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
    )
    return {
        "items": files,
        "total": total,
    }


@router.get(
    "/files/{file_id}",
    response_model=FileResponse,
    summary="Get File Metadata",
)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Fetch metadata and processing state of a specific file.
    """
    file_record = file_service.get_file(db=db, file_id=file_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found",
        )
    return file_record


@router.get(
    "/files/{file_id}/download",
    summary="Download File Stream",
)
def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Stream physical file content from disk storage.
    """
    file_record = file_service.get_file(db=db, file_id=file_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found",
        )

    disk_path = Path(file_record.filepath)
    if not disk_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical file not found on disk storage",
        )

    return FastAPIFileresponse(
        path=str(disk_path),
        filename=file_record.filename,
        media_type="application/octet-stream",
    )


@router.patch(
    "/files/{file_id}/status",
    response_model=FileResponse,
    summary="Update File Status (M2M Worker Callback)",
)
def update_file_status(
    file_id: str,
    data: FileStatusUpdate,
    db: Session = Depends(get_db),
    _valid_key: bool = Depends(validate_internal_service_key),
):
    """
    Internal callback for Member 5 & Member 6 workers to update file indexing state.
    Protected via X-Internal-Service-Key.
    """
    updated_file = file_service.update_file_status(
        db=db,
        file_id=file_id,
        new_status=data.status,
        error_message=data.error_message,
    )
    if not updated_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found",
        )
    return updated_file


@router.delete(
    "/files/{file_id}",
    response_model=MessageResponse,
    summary="Delete File",
)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete file metadata and wipe its storage payload from disk.
    """
    success = file_service.delete_file(
        db=db,
        file_id=file_id,
        user_id=current_user.get("id"),
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found",
        )
    return {
        "message": f"File '{file_id}' successfully deleted",
        "success": True,
    }
