from app.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter(tags=["Health"])


@router.get("/health", summary="System Health Check")
def health_check(db: Session = Depends(get_db)):
    """
    Verify application health, service availability, and database connectivity.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity failed: {str(e)}",
        )

    return {
        "status": "healthy",
        "service": "INDUSAI-X Backend",
        "database": db_status,
    }
