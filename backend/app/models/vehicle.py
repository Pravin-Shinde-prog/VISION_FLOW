from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.plate import VehiclePlate
    from app.models.detection import Detection
    from app.models.trajectory import Trajectory
    from app.models.alert import Alert


class Vehicle(Base):
    """
    Represents a distinct physical vehicle entity in the city.
    Decoupled from individual plate detections to support multi-feature visual re-identification
    when plates are obscured, broken, or modified.
    """
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Core visual attributes
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    make: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    window_tint: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    # Flexible visual signature schema (stickers, roof rails, physical damage, embeddings)
    visual_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )

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
    plates: Mapped[List["VehiclePlate"]] = relationship(
        "VehiclePlate",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="vehicle", lazy="selectin")
    trajectories: Mapped[List["Trajectory"]] = relationship("Trajectory", back_populates="vehicle", lazy="selectin")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="vehicle", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id} uid='{self.vehicle_uid}' type='{self.vehicle_type}' color='{self.color}'>"
