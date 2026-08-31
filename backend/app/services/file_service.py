import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import File, Workspace
from app.services.audit_service import log_action
from app.services.workspace_service import get_workspace_dir


def sniff_magic_bytes(header: bytes, ext: str) -> bool:
    """
    Validate magic byte signatures against expected file extensions
    to prevent disguised executables or malicious payloads.
    """
    # Detect known executable signatures immediately
    if header.startswith(b"MZ") or header.startswith(b"\x7fELF"):
        return False

    ext = ext.lower()

    if ext == ".pdf":
        return header.startswith(b"%PDF-")

    if ext == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n") or header.startswith(b"\x89PNG")

    if ext in [".jpg", ".jpeg"]:
        return header.startswith(b"\xFF\xD8\xFF")

    if ext == ".tiff":
        return header.startswith(b"II*\x00") or header.startswith(b"MM\x00*")

    if ext in [".docx", ".pptx", ".xlsx"]:
        # ZIP archive signature used by OOXML documents
        return header.startswith(b"PK\x03\x04") or header.startswith(b"PK\x05\x06")

    if ext in [".csv", ".json", ".txt", ".svg", ".xls"]:
        # Disallow binary NUL bytes in plain text industrial data
        if b"\x00" in header[:256]:
            return False
        return True

    return True


async def save_uploaded_file(
    db: Session,
    workspace_id: str,
    upload_file: UploadFile,
    user_id: str | None = None,
) -> File:
    """
    Validates, stores file on disk using UUID isolation, and creates DB record.
    """
    # Verify workspace existence
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    original_filename = upload_file.filename or "unnamed_file"
    ext = Path(original_filename).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' is not permitted. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read initial chunk for magic-byte sniffing and size verification
    contents = await upload_file.read()
    file_size = len(contents)

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed {settings.MAX_FILE_SIZE_MB}MB limit",
        )

    # Sniff magic bytes
    if not sniff_magic_bytes(contents[:32], ext):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match declared extension or contains unauthorized binary signatures",
        )

    file_id = str(uuid.uuid4())
    safe_disk_name = f"{file_id}{ext}"
    ws_dir = get_workspace_dir(workspace_id)
    dest_path = ws_dir / safe_disk_name

    # Write securely to disk
    dest_path.write_bytes(contents)

    # Determine standard file type category
    file_type = ext.lstrip(".").lower()

    # Create DB record
    file_record = File(
        id=file_id,
        workspace_id=workspace_id,
        filename=original_filename,
        filepath=str(dest_path),
        file_type=file_type,
        size=file_size,
        status="uploaded",
        uploaded_by=user_id,
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    # Log audit event
    log_action(
        db=db,
        action="UPLOAD_FILE",
        resource="file",
        user_id=user_id,
        workspace_id=workspace_id,
        details={
            "file_id": file_id,
            "filename": original_filename,
            "file_type": file_type,
            "size": file_size,
        },
    )

    return file_record


def get_file(db: Session, file_id: str) -> File | None:
    """Retrieve file metadata by ID."""
    return db.query(File).filter(File.id == file_id).first()


def list_workspace_files(
    db: Session,
    workspace_id: str,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[File], int]:
    """Retrieve paginated files for a workspace."""
    query = db.query(File).filter(File.workspace_id == workspace_id)
    total = query.count()
    files = query.offset(skip).limit(limit).all()
    return files, total


def update_file_status(
    db: Session,
    file_id: str,
    new_status: str,
    error_message: str | None = None,
) -> File | None:
    """Update file processing status (M2M worker callback)."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        return None

    file_record.status = new_status
    if error_message:
        file_record.error_message = error_message
    db.commit()
    db.refresh(file_record)

    # Audit log
    log_action(
        db=db,
        action="UPDATE_FILE_STATUS",
        resource="file",
        workspace_id=file_record.workspace_id,
        details={
            "file_id": file_id,
            "filename": file_record.filename,
            "status": new_status,
            "error_message": error_message,
        },
    )

    return file_record


def delete_file(
    db: Session,
    file_id: str,
    user_id: str | None = None,
) -> bool:
    """Deletes a file record, removes physical storage, and records audit."""
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        return False

    ws_id = file_record.workspace_id
    filename = file_record.filename
    disk_path = Path(file_record.filepath)

    log_action(
        db=db,
        action="DELETE_FILE",
        resource="file",
        user_id=user_id,
        workspace_id=ws_id,
        details={"file_id": file_id, "filename": filename},
    )

    db.delete(file_record)
    db.commit()

    if disk_path.exists():
        try:
            disk_path.unlink()
        except OSError:
            pass

    return True
