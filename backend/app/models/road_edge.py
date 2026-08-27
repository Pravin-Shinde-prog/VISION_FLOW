from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, Integer, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.camera import Camera


class RoadEdge(Base):
    """
    Represents a DIRECTED topological connection between two camera nodes in the urban road graph.
    Used by the Spatio-Temporal Graph Engine to validate physical travel feasibility and detect ghost plates.
    """
    __tablename__ = "road_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    destination_camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Physical road metrics
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False)
    expected_min_travel_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    expected_max_travel_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speed_limit_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    road_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    source_camera: Mapped["Camera"] = relationship(
        "Camera",
        foreign_keys=[source_camera_id],
        back_populates="outgoing_edges",
        lazy="selectin"
    )
    destination_camera: Mapped["Camera"] = relationship(
        "Camera",
        foreign_keys=[destination_camera_id],
        back_populates="incoming_edges",
        lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("source_camera_id != destination_camera_id", name="check_no_self_loop_edge"),
        UniqueConstraint("source_camera_id", "destination_camera_id", name="uq_source_destination_edge"),
        Index("ix_road_edges_source_dest", "source_camera_id", "destination_camera_id"),
    )

    def __repr__(self) -> str:
        return f"<RoadEdge id={self.id} {self.source_camera_id}->{self.destination_camera_id} dist={self.distance_meters}m>"
