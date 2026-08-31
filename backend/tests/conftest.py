import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

import backend.app.db.database as db_module
from backend.app.core.config import settings
from backend.app.db.database import Base, get_db
from backend.app.main import create_app


@pytest.fixture(scope="session")
def temp_storage_root():
    """Create a temporary storage root for the entire test session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        settings.STORAGE_DIR = tmp_path
        (tmp_path / "workspaces").mkdir(parents=True, exist_ok=True)
        yield tmp_path


@pytest.fixture(scope="function")
def test_db_engine(temp_storage_root):
    """Create an isolated temporary SQLite database for each test."""
    db_file = temp_storage_root / f"test_{os.getpid()}_{id(temp_storage_root)}.db"
    test_db_url = f"sqlite:///{db_file}"

    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if db_file.exists():
        try:
            db_file.unlink()
        except OSError:
            pass


@pytest.fixture(scope="function")
def db_session(test_db_engine, monkeypatch):
    """Provide a database session for direct model manipulation in tests."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    monkeypatch.setattr(db_module, "engine", test_db_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(settings, "DATABASE_URL", str(test_db_engine.url))
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db_engine, temp_storage_root, monkeypatch):
    """Provide a FastAPI TestClient with overridden database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(db_module, "engine", test_db_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(settings, "DATABASE_URL", str(test_db_engine.url))

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_bytes():
    return b"%PDF-1.4\n1 0 obj\n<< /Title (Pump Maintenance Manual) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"


@pytest.fixture
def sample_png_bytes():
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"


@pytest.fixture
def sample_csv_bytes():
    return b"timestamp,inboard_temp_c,vibration_rms,lube_oil_bar\n2026-08-30T14:15:00Z,72.1,2.3,0.4\n2026-08-30T14:22:00Z,104.2,6.8,0.3\n2026-08-30T14:35:12Z,108.5,9.82,0.2\n"


@pytest.fixture
def sample_fake_exe_bytes():
    return b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00"
