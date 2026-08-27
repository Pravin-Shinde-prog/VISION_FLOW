from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.detection import Detection
    from app.models.camera import Camera


class Alert(Base):
    """
    Represents real-time law enforcement & safety operational alerts.
    """
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="high", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True, nullable=False)

    plate_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)

    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    detection_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("detections.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    camera_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="alerts", lazy="selectin")
    detection: Mapped[Optional["Detection"]] = relationship("Detection", back_populates="alerts", lazy="selectin")
    camera: Mapped[Optional["Camera"]] = relationship("Camera", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} type='{self.alert_type}' severity='{self.severity}' status='{self.status}'>"
