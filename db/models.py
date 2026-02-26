import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    BigInteger,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


# =========================
# ENUMS
# =========================

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# =========================
# USERS TABLE (Optional)
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), default="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="user", cascade="all, delete")


# =========================
# JOBS TABLE
# =========================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,  # auth not required for MVP
    )

    project_name = Column(String(255))

    original_image_path = Column(Text, nullable=False)
    annotated_image_path = Column(Text)
    thumbnail_image_path = Column(Text)

    status = Column(
        Enum(JobStatus, name="job_status"),
        nullable=False,
    )

    image_width = Column(Integer)
    image_height = Column(Integer)

    total_detections = Column(Integer, default=0)

    model_version = Column(String(100))
    processing_time_ms = Column(Integer)

    error_code = Column(String(100))
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="jobs")
    detections = relationship("Detection", back_populates="job", cascade="all, delete")
    estimation = relationship("Estimation", back_populates="job", uselist=False, cascade="all, delete")


# =========================
# DETECTIONS TABLE
# =========================

class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)

    bbox_x1 = Column(Integer, nullable=False)
    bbox_y1 = Column(Integer, nullable=False)
    bbox_x2 = Column(Integer, nullable=False)
    bbox_y2 = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="detections")


# =========================
# ESTIMATIONS TABLE
# =========================

class Estimation(Base):
    __tablename__ = "estimations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    total_symbols = Column(Integer, nullable=False)
    grand_total_cost = Column(BigInteger, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="estimation")
    items = relationship("EstimationItem", back_populates="estimation", cascade="all, delete")


# =========================
# ESTIMATION ITEMS TABLE
# =========================

class EstimationItem(Base):
    __tablename__ = "estimation_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    estimation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("estimations.id", ondelete="CASCADE"),
        nullable=False,
    )

    symbol = Column(String(100), nullable=False)
    count = Column(Integer, nullable=False)
    unit_cost = Column(BigInteger, nullable=False)
    total_cost = Column(BigInteger, nullable=False)

    estimation = relationship("Estimation", back_populates="items")


# =========================
# MESSAGE LOGS (Future RabbitMQ)
# =========================

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(100), nullable=False)
    message_hash = Column(Text, nullable=False)

    processed_at = Column(DateTime(timezone=True), server_default=func.now())