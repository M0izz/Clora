from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class IngestionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_id: str
    workspace_id: str
    filename: str
    status: str  # QUEUED, PROCESSING, INDEXING, COMPLETED, FAILED
    progress: int
    chunks_count: Optional[int] = 0
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class IngestionJobListResponse(BaseModel):
    jobs: list[IngestionJobResponse]
    total: int
