from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Float, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.road_edge import RoadEdge
    from app.models.detection import Detection
    from app.models.trajectory import TrajectoryEvent


class Camera(Base):
    """
    Represents a physical or simulated ANPR/CCTV camera node in the urban network.
    Uses PostGIS Geometry(POINT, 4326) for geospatial positioning and spatial queries.
    SRID 4326 represents standard WGS 84 (GPS latitude/longitude in degrees).
    """
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Coordinates and PostGIS Point geometry (SRID 4326 = WGS 84)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )

    # Orientation & location context
    direction_angle: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Heading angle (0-360 degrees)
    road_name: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True, nullable=False)

    # Flexible metadata (camera mount height, lens specs, stream URL, resolution)
    installation_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

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

    # Relationships (configured with lazy="selectin" for clean async resolution)
    outgoing_edges: Mapped[List["RoadEdge"]] = relationship(
        "RoadEdge",
        foreign_keys="RoadEdge.source_camera_id",
        back_populates="source_camera",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    incoming_edges: Mapped[List["RoadEdge"]] = relationship(
        "RoadEdge",
        foreign_keys="RoadEdge.destination_camera_id",
        back_populates="destination_camera",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="camera", lazy="selectin")
    trajectory_events: Mapped[List["TrajectoryEvent"]] = relationship("TrajectoryEvent", back_populates="camera", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Camera id={self.id} camera_id='{self.camera_id}' name='{self.name}' status='{self.status}'>"
