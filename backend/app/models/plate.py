from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.detection import Detection


class VehiclePlate(Base):
    """
    Represents an observed vehicle license plate and its association with a Vehicle entity.
    Supports plate changes, anomaly tracking, and unverified plate states.
    """
    __tablename__ = "vehicle_plates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    normalized_plate: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    raw_plate_text: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    state_code: Mapped[Optional[str]] = mapped_column(String(8), index=True, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="valid", index=True, nullable=False)

    anomaly_flags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
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
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="plates", lazy="selectin")
    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="plate", lazy="selectin")

    def __repr__(self) -> str:
        return f"<VehiclePlate id={self.id} plate='{self.normalized_plate}' status='{self.status}'>"
