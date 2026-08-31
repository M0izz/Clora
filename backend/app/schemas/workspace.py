from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Workspace display name")
    description: str | None = Field(None, max_length=2000, description="Optional description of the industrial unit")


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str | None = None
    created_at: datetime
    files_count: int = 0
    queries_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class WorkspaceListResponse(BaseModel):
    items: list[WorkspaceResponse]
    total: int
