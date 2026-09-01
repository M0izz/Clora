from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileResponse(BaseModel):
    id: str
    workspace_id: str
    filename: str
    file_type: str
    size: int
    status: str  # uploaded, processing, indexed, failed
    uploaded_by: str | None = None
    error_message: str | None = None
    ingestion_job_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    items: list[FileResponse]
    total: int


class FileStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: 'processing', 'indexed', or 'failed'")
    error_message: str | None = Field(None, description="Optional error message if indexing failed")
