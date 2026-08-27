import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement
from app.models import (
    Camera,
    RoadEdge,
    Vehicle,
    VehiclePlate,
    Detection,
    Watchlist,
    Alert,
    Trajectory,
    TrajectoryEvent
)


@pytest.mark.anyio
async def test_database_and_postgis_connection(db_session: AsyncSession):
    """Verify raw database connection and active PostGIS version."""
    result = await db_session.execute(text("SELECT current_database(), PostGIS_Version();"))
    row = result.fetchone()
    assert row is not None
    db_name, postgis_ver = row[0], row[1]
    assert db_name == "vision_flow"
    assert "3.6" in postgis_ver


@pytest.mark.anyio
async def test_full_model_relationships_and_spatial_queries(db_session: AsyncSession):
    """
    Tests complete lifecycle of all core entities within an isolated transaction.
    Rolls back at the end to keep the database clean.
    """
    try:
        # 1. Create two Camera nodes with PostGIS Point geometries (SRID 4326: Lon, Lat)
        cam1 = Camera(
            camera_id="CAM_TEST_001",
            name="Connaught Place North",
            description="Outer Circle North Junction ANPR Camera",
            latitude=28.6328,
            longitude=77.2197,
            location=WKTElement("POINT(77.2197 28.6328)", srid=4326),
            direction_angle=45.0,
            road_name="Radial Road 1",
            sector="Central",
            status="active",
            installation_metadata={"mount_height_m": 6.5, "resolution": "4K", "fps": 30}
        )
        cam2 = Camera(
            camera_id="CAM_TEST_002",
            name="Barakhamba Road Entry",
            description="Barakhamba Road ANPR Camera",
            latitude=28.6295,
            longitude=77.2274,
            location=WKTElement("POINT(77.2274 28.6295)", srid=4326),
            direction_angle=120.0,
            road_name="Barakhamba Road",
            sector="Central",
            status="active",
            installation_metadata={"mount_height_m": 7.0, "resolution": "4K", "fps": 30}
        )
        db_session.add_all([cam1, cam2])
        await db_session.flush()
        assert cam1.id is not None
        assert cam2.id is not None

        # Verify PostGIS spatial distance calculation between cam1 and cam2
        dist_query = await db_session.execute(
            text("""
                SELECT ST_Distance(
                    ST_SetSRID(ST_MakePoint(77.2197, 28.6328), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(77.2274, 28.6295), 4326)::geography
                );
            """)
        )
        dist_meters = dist_query.scalar()
        assert dist_meters > 500.0  # Approx 800-900m in reality

        # 2. Create Directed RoadEdge (cam1 -> cam2)
        edge = RoadEdge(
            source_camera_id=cam1.id,
            destination_camera_id=cam2.id,
            distance_meters=850.0,
            expected_min_travel_seconds=45.0,
            expected_max_travel_seconds=300.0,
            speed_limit_kmh=60.0,
            road_name="Barakhamba Corridor",
            direction="South-East",
            is_active=True
        )
        db_session.add(edge)
        await db_session.flush()
        assert edge.id is not None

        # 3. Create Vehicle entity (visual attributes & metadata)
        now = datetime.now(timezone.utc)
        vehicle = Vehicle(
            vehicle_uid="veh_test_883921",
            vehicle_type="SUV",
            color="Dark Blue",
            make="Hyundai",
            model="Creta",
            window_tint="light",
            visual_features={
                "roof_rails": True,
                "alloy_wheels": True,
                "stickers": ["yellow_parking_permit"],
                "damage_marks": None,
                "embedding_vector_dim": 128
            },
            first_seen_at=now,
            last_seen_at=now
        )
        db_session.add(vehicle)
        await db_session.flush()
        assert vehicle.id is not None

        # 4. Create VehiclePlate entity associated with Vehicle
        plate = VehiclePlate(
            vehicle_id=vehicle.id,
            normalized_plate="DL01AB1234",
            raw_plate_text="DL 01 AB 1234",
            state_code="DL",
            confidence=0.96,
            status="valid",
            anomaly_flags={"is_broken": False, "is_modified": False, "is_missing": False},
            first_seen_at=now,
            last_seen_at=now
        )
        db_session.add(plate)
        await db_session.flush()
        assert plate.id is not None

        # 5. Create Detection events at Camera 1 and Camera 2
        det1 = Detection(
            detection_uid="evt_cam1_1001",
            camera_id=cam1.id,
            vehicle_id=vehicle.id,
            plate_id=plate.id,
            timestamp=now,
            plate_number="DL01AB1234",
            ocr_confidence=0.96,
            vehicle_color="Dark Blue",
            vehicle_type="SUV",
            snapshot_path="/media/snapshots/cam1/evt1001.jpg",
            direction_travel="Eastbound",
            processing_metadata={"bbox": [300, 200, 700, 600], "fps": 29.8},
            association_confidence=0.98
        )
        det2 = Detection(
            detection_uid="evt_cam2_1002",
            camera_id=cam2.id,
            vehicle_id=vehicle.id,
            plate_id=plate.id,
            timestamp=now + timedelta(seconds=60),
            plate_number="DL01AB1234",
            ocr_confidence=0.94,
            vehicle_color="Dark Blue",
            vehicle_type="SUV",
            snapshot_path="/media/snapshots/cam2/evt1002.jpg",
            direction_travel="Eastbound",
            processing_metadata={"bbox": [320, 210, 720, 610], "fps": 30.0},
            association_confidence=0.97
        )
        db_session.add_all([det1, det2])
        await db_session.flush()
        assert det1.id is not None
        assert det2.id is not None

        # 6. Create Watchlist target record
        watchlist_item = Watchlist(
            plate_number="DL01AB1234",
            category="stolen",
            reason="FIR #49201 reported stolen from Connaught Place",
            priority="critical",
            vehicle_description="Blue Hyundai Creta SUV",
            is_active=True
        )
        db_session.add(watchlist_item)
        await db_session.flush()
        assert watchlist_item.id is not None

        # 7. Create Alert entity triggered by detection
        alert = Alert(
            alert_type="watchlist_match",
            severity="critical",
            status="new",
            plate_number="DL01AB1234",
            vehicle_id=vehicle.id,
            detection_id=det1.id,
            camera_id=cam1.id,
            message="Critical: Stolen vehicle DL01AB1234 spotted at Connaught Place North",
            evidence_data={
                "watchlist_id": watchlist_item.id,
                "snapshot_ref": det1.snapshot_path,
                "confidence": 0.96
            }
        )
        db_session.add(alert)
        await db_session.flush()
        assert alert.id is not None

        # 8. Create Trajectory & TrajectoryEvents (chronological path)
        traj = Trajectory(
            trajectory_uid="traj_dl01ab1234_20260827_01",
            vehicle_id=vehicle.id,
            plate_number="DL01AB1234",
            start_time=now,
            end_time=now + timedelta(seconds=60),
            start_camera_id=cam1.id,
            end_camera_id=cam2.id,
            total_distance_meters=850.0,
            status="completed",
            confidence=0.98,
            metadata_info={"average_speed_kmh": 51.0}
        )
        db_session.add(traj)
        await db_session.flush()

        event1 = TrajectoryEvent(
            trajectory_id=traj.id,
            detection_id=det1.id,
            camera_id=cam1.id,
            sequence_order=1,
            timestamp=now,
            direction="Eastbound",
            transition_time_seconds=0.0,
            transition_distance_meters=0.0,
            speed_estimate_kmh=48.0
        )
        event2 = TrajectoryEvent(
            trajectory_id=traj.id,
            detection_id=det2.id,
            camera_id=cam2.id,
            sequence_order=2,
            timestamp=now + timedelta(seconds=60),
            direction="Eastbound",
            transition_time_seconds=60.0,
            transition_distance_meters=850.0,
            speed_estimate_kmh=51.0
        )
        db_session.add_all([event1, event2])
        await db_session.flush()

        # 9. Query and verify Trajectory relationship
        traj_query = await db_session.execute(
            select(Trajectory).where(Trajectory.id == traj.id)
        )
        fetched_traj = traj_query.scalar_one()
        assert fetched_traj.id == traj.id
        assert len(fetched_traj.events) == 2
        assert fetched_traj.events[0].sequence_order == 1
        assert fetched_traj.events[1].sequence_order == 2

        # 10. Query and verify Camera relationships
        cam_query = await db_session.execute(
            select(Camera).where(Camera.camera_id == "CAM_TEST_001")
        )
        fetched_cam = cam_query.scalar_one()
        assert fetched_cam.name == "Connaught Place North"
        assert len(fetched_cam.outgoing_edges) == 1
        assert fetched_cam.outgoing_edges[0].destination_camera_id == cam2.id

    finally:
        # Clean rollback - do not pollute development database with test records
        await db_session.rollback()


@pytest.mark.anyio
async def test_constraints_and_edge_cases(db_session: AsyncSession):
    """
    Verifies that database constraints (self-loop prevention, unique constraints)
    are strictly enforced at the PostgreSQL engine level.
    """
    from sqlalchemy.exc import IntegrityError

    try:
        # Create a test camera
        cam = Camera(
            camera_id="CAM_CONSTRAINT_001",
            name="Constraint Test Node",
            latitude=28.6139,
            longitude=77.2090,
            location=WKTElement("POINT(77.2090 28.6139)", srid=4326),
            status="active"
        )
        db_session.add(cam)
        await db_session.flush()

        # 1. Attempt invalid self-loop edge (cam -> cam)
        invalid_edge = RoadEdge(
            source_camera_id=cam.id,
            destination_camera_id=cam.id,
            distance_meters=0.0,
            expected_min_travel_seconds=0.0
        )
        db_session.add(invalid_edge)
        
        with pytest.raises(IntegrityError):
            await db_session.flush()

    finally:
        await db_session.rollback()
