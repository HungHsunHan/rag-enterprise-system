import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy

from app.main import app
from app.db.database import get_db, Base
from app.core.config import settings

# Create test database engine
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/hr_chatbot_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Override database dependency for testing
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """
    Create test client with test database
    """
    # Enable required PostgreSQL extensions
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """
    Create test database session
    """
    # Enable required PostgreSQL extensions
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        conn.execute(sqlalchemy.text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)