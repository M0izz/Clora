import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="engineer")  # admin, engineer, viewer
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    files = relationship(
        "File",
        back_populates="workspace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    queries = relationship(
        "Query",
        back_populates="workspace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class File(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
        index=True,
    )  # uploaded, processing, indexed, failed
    uploaded_by = Column(String(36), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    workspace = relationship("Workspace", back_populates="files")


class Query(Base):
    __tablename__ = "queries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(String(36), nullable=True)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True, default=list)  # list of citation objects
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workspace = relationship("Workspace", back_populates="queries")
    agent_tasks = relationship(
        "AgentTask",
        back_populates="query",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AgentTask.created_at",
    )


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    query_id = Column(
        String(36),
        ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name = Column(String(100), nullable=False)  # triage_agent, document_agent, tabular_agent, synthesis_agent
    input_data = Column(JSON, nullable=True, default=dict)
    output_data = Column(JSON, nullable=True, default=dict)
    status = Column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    query = relationship("Query", back_populates="agent_tasks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True, index=True)
    workspace_id = Column(String(36), nullable=True, index=True)  # Decoupled to persist beyond workspace deletion
    action = Column(String(100), nullable=False, index=True)  # CREATE_WORKSPACE, UPLOAD_FILE, DISPATCH_QUERY, etc.
    resource = Column(String(100), nullable=False)  # workspace, file, query, system
    details = Column(JSON, nullable=True, default=dict)  # Snapshots of workspace_name, file_name, etc.
    timestamp = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
