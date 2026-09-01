import asyncio
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi import (
    Query as QueryParam,
)
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import AgentTask, Query, Workspace
from backend.app.schemas.query import (
    AgentTaskResponse,
    QueryCreate,
    QueryListResponse,
    QueryPollResponse,
)
from backend.app.services import agent_service
from backend.app.services.audit_service import log_action

router = APIRouter(tags=["Queries"])


@router.post(
    "/query",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispatch Industrial Investigation Query",
)
async def dispatch_query(
    data: QueryCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    sync: bool = QueryParam(False, description="Debug only synchronous execution mode"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit an industrial intelligence question.
    By default returns 202 Accepted with a poll_url for asynchronous multi-agent processing.
    When ?sync=true is requested (and DEBUG=True), executes with a strict 15-second timeout.
    """
    # Verify workspace existence
    workspace = db.query(Workspace).filter(Workspace.id == data.workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{data.workspace_id}' not found",
        )

    # Initialize Query DB record
    query_id = str(uuid.uuid4())
    query_record = Query(
        id=query_id,
        workspace_id=data.workspace_id,
        user_id=current_user.get("id"),
        question=data.question.strip(),
        status="processing",
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    # Log audit event
    log_action(
        db=db,
        action="DISPATCH_QUERY",
        resource="query",
        user_id=current_user.get("id"),
        workspace_id=data.workspace_id,
        details={
            "query_id": query_id,
            "question": data.question,
            "sync": sync,
        },
    )

    poll_url = f"/api/query/{query_id}"

    if sync:
        if not settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Synchronous query execution is restricted to DEBUG mode",
            )
        try:
            await asyncio.wait_for(
                agent_service.execute_query_task(query_id),
                timeout=settings.SYNC_QUERY_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Synchronous execution exceeded timeout of {settings.SYNC_QUERY_TIMEOUT_SEC}s",
            )

        # Refresh from DB with fresh query
        db.expire_all()
        fresh_query = db.query(Query).filter(Query.id == query_id).first()
        tasks = (
            db.query(AgentTask)
            .filter(AgentTask.query_id == query_id)
            .order_by(AgentTask.created_at.asc())
            .all()
        )
        response.status_code = status.HTTP_200_OK
        return {
            "query_id": fresh_query.id,
            "status": fresh_query.status,
            "poll_url": poll_url,
            "question": fresh_query.question,
            "response": fresh_query.response,
            "sources": fresh_query.sources or [],
            "agent_tasks": [
                AgentTaskResponse.model_validate(t) for t in tasks
            ],
            "created_at": fresh_query.created_at,
            "completed_at": fresh_query.completed_at,
            "error_message": fresh_query.error_message,
        }

    # Asynchronous background execution
    background_tasks.add_task(agent_service.execute_query_task, query_id)

    return {
        "query_id": query_record.id,
        "status": query_record.status,
        "poll_url": poll_url,
        "question": query_record.question,
        "response": None,
        "sources": [],
        "agent_tasks": [],
        "created_at": query_record.created_at,
        "completed_at": None,
        "error_message": None,
    }


@router.get(
    "/query/{query_id}",
    response_model=QueryPollResponse,
    summary="Poll Query Execution Status & Citations",
)
def poll_query(
    query_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Poll live execution status, sub-agent intermediate traces, final answers, and citations.
    """
    query_record = db.query(Query).filter(Query.id == query_id).first()
    if not query_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query '{query_id}' not found",
        )

    tasks = (
        db.query(AgentTask)
        .filter(AgentTask.query_id == query_id)
        .order_by(AgentTask.created_at.asc())
        .all()
    )

    return {
        "query_id": query_record.id,
        "status": query_record.status,
        "poll_url": f"/api/query/{query_record.id}",
        "question": query_record.question,
        "response": query_record.response,
        "sources": query_record.sources or [],
        "agent_tasks": [AgentTaskResponse.model_validate(t) for t in tasks],
        "created_at": query_record.created_at,
        "completed_at": query_record.completed_at,
        "error_message": query_record.error_message,
    }


@router.get(
    "/workspaces/{workspace_id}/queries",
    response_model=QueryListResponse,
    summary="List Workspace Queries",
)
def list_workspace_queries(
    workspace_id: str,
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List historical queries and forensic analyses conducted within a workspace.
    """
    query = db.query(Query).filter(Query.workspace_id == workspace_id).order_by(Query.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {
        "items": items,
        "total": total,
    }


# ============================================================================
# Investigation Session Aliases & DOCX Export
# ============================================================================

@router.post(
    "/investigations",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispatch Investigation (Alias for /api/query)",
)
async def dispatch_investigation(
    data: QueryCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    sync: bool = QueryParam(False, description="Debug only synchronous execution mode"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return await dispatch_query(
        data=data,
        background_tasks=background_tasks,
        response=response,
        sync=sync,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/investigations/{investigation_id}",
    response_model=QueryPollResponse,
    summary="Poll Investigation Status (Alias for /api/query/{id})",
)
def poll_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return poll_query(
        query_id=investigation_id,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/query/{query_id}/export-docx",
    summary="Export Technical Approval Note as DOCX",
)
def export_query_docx(
    query_id: str,
    db: Session = Depends(get_db),
):
    """
    Generates and downloads a standardized MRPL Executive Approval Note in DOCX format.
    """
    query_record = db.query(Query).filter(Query.id == query_id).first()
    if not query_record or not query_record.response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Completed query '{query_id}' not found",
        )

    try:
        from data_intelligence.docx_generator import ApprovalNoteGenerator, ApprovalNoteInput
        generator = ApprovalNoteGenerator()
        doc_input = ApprovalNoteInput(
            title=f"Investigation: {query_record.question[:60]}",
            equipment_tag="Refinery Asset",
            executive_summary=query_record.response[:300],
            root_cause_analysis=query_record.response,
            recommendations=["Follow SOP corrective maintenance procedures.", "Inspect valve calibration."],
            citations=[s.get("filename", "Doc") for s in (query_record.sources or [])],
        )
        doc_bytes = generator.generate_bytes(doc_input)
        from fastapi.responses import Response as FastAPIBinaryResponse
        return FastAPIBinaryResponse(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=MRPL_Approval_Note_{query_id[:8]}.docx"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX document: {e}",
        )

