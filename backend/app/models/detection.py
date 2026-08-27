from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, Integer, BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.vehicle import Vehicle
    from app.models.plate import VehiclePlate
    from app.models.alert import Alert
    from app.models.trajectory import TrajectoryEvent


class Detection(Base):
    """
    Represents an individual observation/sighting emitted by a camera.
    Foundation for ANPR, vehicle tracking, trajectory reconstruction, and traffic analytics.
    """
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    detection_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="RESTRICT"),
        index=True,
        nullable=False
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    plate_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("vehicle_plates.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    plate_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    snapshot_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    direction_travel: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    plate_anomaly_flags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    processing_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    association_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="detections", lazy="selectin")
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="detections", lazy="selectin")
    plate: Mapped[Optional["VehiclePlate"]] = relationship("VehiclePlate", back_populates="detections", lazy="selectin")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="detection", lazy="selectin")
    trajectory_events: Mapped[List["TrajectoryEvent"]] = relationship("TrajectoryEvent", back_populates="detection", lazy="selectin")

    __table_args__ = (
        Index("ix_detections_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_detections_plate_timestamp", "plate_number", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Detection id={self.id} uid='{self.detection_uid}' cam={self.camera_id} plate='{self.plate_number}'>"
