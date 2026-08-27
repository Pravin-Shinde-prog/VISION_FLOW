from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, Integer, BigInteger, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base


class GhostPlateAlert(Base):
    """
    Represents detected Ghost / Cloned Plate physical or topological anomaly alerts.
    """
    __tablename__ = "ghost_plate_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    alert_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    plate_number: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    normalized_plate: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="NEW", index=True, nullable=False)

    source_camera_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    target_camera_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    source_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    target_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    observed_delta_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_feasible_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False)
    required_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, nullable=False)

    graph_status: Mapped[str] = mapped_column(String(64), nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    evidence_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    source_snapshot_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_snapshot_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    operator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_ghost_plate_plate_time", "normalized_plate", "created_at"),
        Index("ix_ghost_plate_severity_status", "severity", "status"),
    )

    def __repr__(self) -> str:
        return f"<GhostPlateAlert id={self.id} plate='{self.normalized_plate}' type='{self.alert_type}' severity='{self.severity}'>"
