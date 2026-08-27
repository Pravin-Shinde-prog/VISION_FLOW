from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, Integer, BigInteger, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.camera import Camera
    from app.models.detection import Detection


class Trajectory(Base):
    """
    Represents reconstructed vehicle movement over time across consecutive camera nodes.
    """
    __tablename__ = "trajectories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trajectory_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    plate_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    start_camera_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="SET NULL"),
        nullable=True
    )
    end_camera_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="SET NULL"),
        nullable=True
    )

    total_distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="in_progress", index=True, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="trajectories", lazy="selectin")
    start_camera: Mapped[Optional["Camera"]] = relationship("Camera", foreign_keys=[start_camera_id], lazy="selectin")
    end_camera: Mapped[Optional["Camera"]] = relationship("Camera", foreign_keys=[end_camera_id], lazy="selectin")
    events: Mapped[List["TrajectoryEvent"]] = relationship(
        "TrajectoryEvent",
        back_populates="trajectory",
        order_by="TrajectoryEvent.sequence_order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Trajectory id={self.id} uid='{self.trajectory_uid}' status='{self.status}' start='{self.start_time}'>"


class TrajectoryEvent(Base):
    """
    Represents an individual ordered node/observation in a vehicle trajectory.
    """
    __tablename__ = "trajectory_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trajectory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trajectories.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    detection_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("detections.id", ondelete="SET NULL"),
        nullable=True
    )
    camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="RESTRICT"),
        nullable=False
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    direction: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    transition_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transition_distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speed_estimate_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    trajectory: Mapped["Trajectory"] = relationship("Trajectory", back_populates="events", lazy="selectin")
    detection: Mapped[Optional["Detection"]] = relationship("Detection", back_populates="trajectory_events", lazy="selectin")
    camera: Mapped["Camera"] = relationship("Camera", back_populates="trajectory_events", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("trajectory_id", "sequence_order", name="uq_trajectory_sequence_order"),
        Index("ix_trajectory_events_traj_seq", "trajectory_id", "sequence_order"),
    )

    def __repr__(self) -> str:
        return f"<TrajectoryEvent id={self.id} traj={self.trajectory_id} seq={self.sequence_order} cam={self.camera_id}>"
