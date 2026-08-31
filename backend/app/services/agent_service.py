import uuid
from datetime import datetime, timezone

from app.db import database
from app.db.models import AgentTask, File, Query
from app.integrations.agent_client import agent_client
from app.integrations.rag_client import rag_client
from app.integrations.vision_client import vision_client
from app.services.audit_service import log_action
from sqlalchemy.orm import Session


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def recover_zombie_queries(db: Session) -> int:
    """
    Startup sweep: identifies queries left in 'processing' or 'pending' state
    from previous server shutdowns and transitions them to 'failed'.
    """
    stuck_queries = (
        db.query(Query)
        .filter(Query.status.in_(["processing", "pending"]))
        .all()
    )

    count = len(stuck_queries)
    for q in stuck_queries:
        q.status = "failed"
        q.error_message = "Server restarted during processing. Please resubmit query."
        q.completed_at = get_utc_now()

    if count > 0:
        db.commit()
        log_action(
            db=db,
            action="RECOVER_ZOMBIE_QUERIES",
            resource="system",
            details={"recovered_count": count},
        )

    return count


def create_agent_task(
    db: Session,
    query_id: str,
    agent_name: str,
    input_data: dict,
) -> AgentTask:
    """Creates a tracking record for a specialized agent sub-task."""
    task = AgentTask(
        id=str(uuid.uuid4()),
        query_id=query_id,
        agent_name=agent_name,
        input_data=input_data,
        status="processing",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def complete_agent_task(
    db: Session,
    task: AgentTask,
    output_data: dict,
    status: str = "completed",
) -> None:
    """Marks an agent sub-task as completed with its output artifacts."""
    task.output_data = output_data
    task.status = status
    task.completed_at = get_utc_now()
    db.commit()


async def execute_query_task(query_id: str) -> None:
    """
    Asynchronous query execution worker invoked by FastAPI BackgroundTasks.
    Opens its own isolated DB session, runs multi-agent coordination,
    records intermediate task traces, and writes immutable citations.
    """
    db: Session = database.SessionLocal()
    try:
        query_record = db.query(Query).filter(Query.id == query_id).first()
        if not query_record:
            return

        query_record.status = "processing"
        db.commit()

        workspace_id = query_record.workspace_id
        question = query_record.question

        # Gather workspace files metadata
        files = db.query(File).filter(File.workspace_id == workspace_id).all()
        files_metadata = [
            {"id": f.id, "filename": f.filename, "file_type": f.file_type, "status": f.status}
            for f in files
        ]

        # 1. Triage Agent Step
        triage_task = create_agent_task(
            db, query_id, "triage_agent", {"question": question, "workspace_id": workspace_id}
        )
        triage_res = await agent_client.run_triage_agent(question, workspace_id)
        complete_agent_task(db, triage_task, triage_res)

        # 2. Document RAG Agent Step
        doc_task = create_agent_task(
            db, query_id, "document_agent", {"question": question, "top_k": 3}
        )
        doc_citations = await rag_client.retrieve_context(
            workspace_id=workspace_id,
            question=question,
            files_metadata=files_metadata,
        )
        complete_agent_task(db, doc_task, {"citations_found": len(doc_citations), "chunks": doc_citations})

        # 3. Tabular / Telemetry Agent Step
        tab_task = create_agent_task(
            db, query_id, "tabular_agent", {"question": question, "workspace_id": workspace_id}
        )
        tab_res = await agent_client.run_tabular_agent(
            question=question,
            workspace_id=workspace_id,
            files_metadata=files_metadata,
        )
        complete_agent_task(db, tab_task, tab_res)

        # 4. Vision / P&ID Diagram Agent Step
        vision_task = create_agent_task(
            db, query_id, "vision_agent", {"question": question, "workspace_id": workspace_id}
        )
        vision_citations = await vision_client.analyze_diagrams(
            workspace_id=workspace_id,
            question=question,
            files_metadata=files_metadata,
        )
        complete_agent_task(db, vision_task, {"citations_found": len(vision_citations), "citations": vision_citations})

        # 5. Synthesis Agent Step
        synthesis_task = create_agent_task(
            db, query_id, "synthesis_agent", {"question": question}
        )
        synthesis_res = await agent_client.run_synthesis_agent(
            question=question,
            triage_data=triage_res,
            doc_citations=doc_citations,
            tab_data=tab_res,
            vision_citations=vision_citations,
        )
        complete_agent_task(db, synthesis_task, {"response_length": len(synthesis_res["response"])})

        # Forensic verification: verify file availability for citations against current DB files
        existing_file_ids = {f.id for f in files}
        final_sources = []
        for src in synthesis_res["sources"]:
            src_copy = dict(src)
            if src_copy.get("file_id") and src_copy["file_id"] not in existing_file_ids:
                src_copy["file_available"] = False
            else:
                src_copy["file_available"] = True
            final_sources.append(src_copy)

        # Finalize Query
        query_record.response = synthesis_res["response"]
        query_record.sources = final_sources
        query_record.status = "completed"
        query_record.completed_at = get_utc_now()
        db.commit()

        # Audit log completion
        log_action(
            db=db,
            action="COMPLETE_QUERY",
            resource="query",
            user_id=query_record.user_id,
            workspace_id=workspace_id,
            details={
                "query_id": query_id,
                "citations_count": len(final_sources),
            },
        )

    except Exception as e:
        query_record = db.query(Query).filter(Query.id == query_id).first()
        if query_record:
            query_record.status = "failed"
            query_record.error_message = str(e)
            query_record.completed_at = get_utc_now()
            db.commit()
    finally:
        db.close()
