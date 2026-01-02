import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ChangeStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"
    simulated = "simulated"
    applying = "applying"
    applied = "applied"
    roll_back = "roll_back"


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    environment: Mapped[str] = mapped_column(String(32), nullable=False)  # staging/prod

    status: Mapped[ChangeStatus] = mapped_column(SAEnum(ChangeStatus), nullable=False, default=ChangeStatus.draft)

    created_by: Mapped[str] = mapped_column(String(120), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    items: Mapped[list["ChangeItem"]] = relationship(back_populates="change", cascade="all, delete-orphan")


class ChangeItem(Base):
    __tablename__ = "change_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("changes.id", ondelete="CASCADE"),
                                                 nullable=False)

    key: Mapped[str] = mapped_column(String(200), nullable=False)
    old_value: Mapped[str] = mapped_column(String(500), nullable=False)
    new_value: Mapped[str] = mapped_column(String(500), nullable=False)

    change: Mapped["Change"] = relationship(back_populates="items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)

    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("changes.id", ondelete="CASCADE"),
                                                 nullable=False)

    score: Mapped[int] = mapped_column(nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # LOW/MEDIUM/HIGH

    blast_radius_json: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class SimulationStatus(str, Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("changes.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[SimulationStatus] = mapped_column(SAEnum(SimulationStatus), nullable=False, default=SimulationStatus.queued)

    report_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
