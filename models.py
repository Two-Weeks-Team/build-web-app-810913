import os
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


def _normalized_database_url() -> str:
    raw = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
    if raw.startswith("postgresql+asyncpg://"):
        raw = raw.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql+psycopg://", 1)
    return raw


def _needs_ssl_connect_args(url: str) -> bool:
    if url.startswith("sqlite"):
        return False
    lowered = url.lower()
    return ("localhost" not in lowered) and ("127.0.0.1" not in lowered)


DATABASE_URL = _normalized_database_url()
if _needs_ssl_connect_args(DATABASE_URL):
    engine = create_engine(DATABASE_URL, future=True, connect_args={"sslmode": "require"})
else:
    engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class PlanningProject(Base):
    __tablename__ = "bwa_planning_projects"

    id = Integer().with_variant(Integer, "sqlite")
    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    name = __import__("sqlalchemy").Column(String(200), nullable=False)
    raw_context = __import__("sqlalchemy").Column(Text, nullable=False)
    preferences = __import__("sqlalchemy").Column(Text, nullable=True)
    status = __import__("sqlalchemy").Column(String(30), nullable=False, default="draft")
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    snapshots = relationship("PlanningSnapshot", back_populates="project", cascade="all, delete-orphan")


class PlanningSnapshot(Base):
    __tablename__ = "bwa_planning_snapshots"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    project_id = __import__("sqlalchemy").Column(Integer, ForeignKey("bwa_planning_projects.id"), nullable=False, index=True)
    version_number = __import__("sqlalchemy").Column(Integer, nullable=False, default=1)
    status = __import__("sqlalchemy").Column(String(30), nullable=False, default="draft")
    summary = __import__("sqlalchemy").Column(Text, nullable=False)
    brief_json = __import__("sqlalchemy").Column(Text, nullable=False)
    score = __import__("sqlalchemy").Column(Integer, nullable=False, default=72)
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("PlanningProject", back_populates="snapshots")
    artifacts = relationship("ArtifactCard", back_populates="snapshot", cascade="all, delete-orphan")


class ArtifactCard(Base):
    __tablename__ = "bwa_artifact_cards"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    snapshot_id = __import__("sqlalchemy").Column(Integer, ForeignKey("bwa_planning_snapshots.id"), nullable=False, index=True)
    card_type = __import__("sqlalchemy").Column(String(50), nullable=False)
    title = __import__("sqlalchemy").Column(String(250), nullable=False)
    body = __import__("sqlalchemy").Column(Text, nullable=False)
    source_quote = __import__("sqlalchemy").Column(Text, nullable=True)
    promoted = __import__("sqlalchemy").Column(Boolean, nullable=False, default=False)
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    snapshot = relationship("PlanningSnapshot", back_populates="artifacts")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
