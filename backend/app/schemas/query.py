from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CitationSource(BaseModel):
    file_id: str | None = None
    filename: str
    file_type: str  # pdf, image, csv, docx, json, etc.
    page: int | None = None
    sheet_or_table: str | None = None
    snippet_or_data: Any | None = None
    confidence: float | None = None
    file_available: bool = True

    model_config = ConfigDict(from_attributes=True)


class AgentTaskResponse(BaseModel):
    id: str
    agent_name: str
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class QueryCreate(BaseModel):
    workspace_id: str = Field(..., description="ID of the workspace to query")
    question: str = Field(..., min_length=1, description="Industrial investigation question or prompt")


class QueryResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str | None = None
    question: str
    response: str | None = None
    sources: list[CitationSource] = []
    status: str  # pending, processing, completed, failed
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    agent_tasks: list[AgentTaskResponse] = []

    model_config = ConfigDict(from_attributes=True)


class QueryPollResponse(BaseModel):
    query_id: str
    status: str
    poll_url: str
    question: str
    response: str | None = None
    sources: list[CitationSource] = []
    agent_tasks: list[AgentTaskResponse] = []
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class QueryListResponse(BaseModel):
    items: list[QueryResponse]
    total: int
