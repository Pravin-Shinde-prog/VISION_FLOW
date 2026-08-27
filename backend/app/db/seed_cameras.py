import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, delete
from geoalchemy2.elements import WKTElement

from app.db.session import async_session_factory
from app.models.camera import Camera
from app.models.road_edge import RoadEdge

# Simulated City: Pune, Maharashtra, India
PUNE_CAMERAS = [
    {
        "camera_id": "CAM_PUN_001",
        "name": "Shivaji Nagar Junction",
        "description": "Outer junction splitting FC Road and JM Road corridors",
        "latitude": 18.5308,
        "longitude": 73.8475,
        "direction_angle": 180.0,
        "road_name": "FC Road / JM Road Split",
        "sector": "Shivaji Nagar",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 7.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_002",
        "name": "Fergusson College Road Entry",
        "description": "Northbound entry to FC Road commercial precinct",
        "latitude": 18.5245,
        "longitude": 73.8415,
        "direction_angle": 170.0,
        "road_name": "FC Road",
        "sector": "Deccan",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 30,
            "lanes_covered": 3,
            "mount_height_m": 6.5,
            "feed_protocol": "RTSP/H.264"
        }
    },
    {
        "camera_id": "CAM_PUN_003",
        "name": "Goodluck Chowk",
        "description": "High-density intersection connecting FC Road & Bhandarkar Road",
        "latitude": 18.5175,
        "longitude": 73.8412,
        "direction_angle": 90.0,
        "road_name": "FC Road / Bhandarkar Rd",
        "sector": "Deccan",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 3,
            "mount_height_m": 7.5,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_004",
        "name": "Deccan Gymkhana Bus Terminal",
        "description": "South terminus and entry to Jangali Maharaj (JM) Road one-way corridor",
        "latitude": 18.5160,
        "longitude": 73.8438,
        "direction_angle": 45.0,
        "road_name": "Jangali Maharaj Road",
        "sector": "Deccan",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 25,
            "lanes_covered": 4,
            "mount_height_m": 6.0,
            "feed_protocol": "RTSP/H.264"
        }
    },
    {
        "camera_id": "CAM_PUN_005",
        "name": "JM Road Mid-Section",
        "description": "Mid-corridor high-speed monitoring node on JM Road",
        "latitude": 18.5230,
        "longitude": 73.8480,
        "direction_angle": 350.0,
        "road_name": "JM Road",
        "sector": "Shivaji Nagar",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 7.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_006",
        "name": "COEP / Sancheti Chowk",
        "description": "Arterial flyover intersection towards Pune Station & Old Highway",
        "latitude": 18.5312,
        "longitude": 73.8550,
        "direction_angle": 110.0,
        "road_name": "Old Mumbai-Pune Highway",
        "sector": "Shivaji Nagar",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 8.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_007",
        "name": "Pune Railway Station Entry",
        "description": "Central transit hub entrance and multi-modal interchange",
        "latitude": 18.5289,
        "longitude": 73.8744,
        "direction_angle": 80.0,
        "road_name": "Station Road",
        "sector": "Camp / Station",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 8.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_008",
        "name": "Koregaon Park North Main Road",
        "description": "Residential and lifestyle boulevard corridor check-point",
        "latitude": 18.5362,
        "longitude": 73.8938,
        "direction_angle": 60.0,
        "road_name": "North Main Road",
        "sector": "Koregaon Park",
        "status": "warning",  # Degraded FPS / network jitter
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 18,
            "lanes_covered": 2,
            "mount_height_m": 6.0,
            "feed_protocol": "RTSP/H.264",
            "warning_note": "Network jitter reported on optical uplink"
        }
    },
    {
        "camera_id": "CAM_PUN_009",
        "name": "Kalyani Nagar Bridge",
        "description": "Mula-Mutha River crossing connector node",
        "latitude": 18.5460,
        "longitude": 73.9025,
        "direction_angle": 30.0,
        "road_name": "Kalyani Nagar Bridge",
        "sector": "Kalyani Nagar",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 7.5,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_010",
        "name": "Viman Nagar / Airport Road Junction",
        "description": "Pune International Airport access route intersection",
        "latitude": 18.5679,
        "longitude": 73.9143,
        "direction_angle": 0.0,
        "road_name": "Airport Road",
        "sector": "Viman Nagar",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 8.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_011",
        "name": "Senapati Bapat Road (SB Road)",
        "description": "IT & educational corridor connecting Shivaji Nagar to SPPU",
        "latitude": 18.5345,
        "longitude": 73.8290,
        "direction_angle": 270.0,
        "road_name": "Senapati Bapat Road",
        "sector": "Shivaji Nagar / SB Road",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 6.5,
            "feed_protocol": "RTSP/H.264"
        }
    },
    {
        "camera_id": "CAM_PUN_012",
        "name": "University Circle / SPPU Chowk",
        "description": "Major grade separator circle connecting Aundh, Baner, and Central Pune",
        "latitude": 18.5529,
        "longitude": 73.8258,
        "direction_angle": 315.0,
        "road_name": "Ganeshkhind Road",
        "sector": "Aundh / University",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 6,
            "mount_height_m": 9.0,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_013",
        "name": "Aundh Parihar Chowk",
        "description": "Core commercial junction in western residential sector",
        "latitude": 18.5602,
        "longitude": 73.8065,
        "direction_angle": 280.0,
        "road_name": "Parihar Chowk",
        "sector": "Aundh",
        "status": "offline",  # Hardware maintenance
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 0,
            "lanes_covered": 3,
            "mount_height_m": 6.0,
            "feed_protocol": "RTSP/H.264",
            "offline_reason": "Scheduled pole maintenance / sensor replacement"
        }
    },
    {
        "camera_id": "CAM_PUN_014",
        "name": "Baner High Street Junction",
        "description": "Western expressway feeder node with high commercial traffic",
        "latitude": 18.5590,
        "longitude": 73.7868,
        "direction_angle": 260.0,
        "road_name": "Baner Road",
        "sector": "Baner",
        "status": "active",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "4K",
            "fps": 30,
            "lanes_covered": 4,
            "mount_height_m": 7.5,
            "feed_protocol": "RTSP/H.265"
        }
    },
    {
        "camera_id": "CAM_PUN_015",
        "name": "Swargate Multi-Modal Transit",
        "description": "Southern gateway connecting intercity bus terminal and highway feeders",
        "latitude": 18.5018,
        "longitude": 73.8586,
        "direction_angle": 180.0,
        "road_name": "Satara Road / Tilak Road",
        "sector": "Swargate",
        "status": "warning",
        "installation_metadata": {
            "is_simulated": True,
            "city": "Pune",
            "resolution": "1080p",
            "fps": 20,
            "lanes_covered": 4,
            "mount_height_m": 7.0,
            "feed_protocol": "RTSP/H.264",
            "warning_note": "Lens condensation warning active"
        }
    }
]

# Directed Topological Road Connections (Source Code -> Destination Code)
ROAD_EDGES_CONFIG = [
    # FC Road & JM Road One-Way Loop System
    ("CAM_PUN_001", "CAM_PUN_002", 1050.0, 75.0, 300.0, 50.0, "FC Road Entrance", "Southbound"),
    ("CAM_PUN_002", "CAM_PUN_003", 800.0, 60.0, 240.0, 40.0, "FC Road Mid-Corridor", "Southbound"),
    ("CAM_PUN_003", "CAM_PUN_004", 420.0, 30.0, 120.0, 40.0, "Deccan Gymkhana Link", "Eastbound"),
    ("CAM_PUN_004", "CAM_PUN_005", 950.0, 70.0, 260.0, 50.0, "JM Road Northbound Arterial", "Northbound"),
    ("CAM_PUN_005", "CAM_PUN_001", 1020.0, 75.0, 280.0, 50.0, "JM Road to Shivaji Nagar Split", "Northbound"),

    # Central to East Corridor (Pune Station, Koregaon Park, Airport)
    ("CAM_PUN_001", "CAM_PUN_006", 880.0, 65.0, 250.0, 50.0, "Sancheti Flyover Link", "Eastbound"),
    ("CAM_PUN_006", "CAM_PUN_007", 2200.0, 150.0, 600.0, 50.0, "Old Highway to Station", "Eastbound"),
    ("CAM_PUN_007", "CAM_PUN_008", 2300.0, 160.0, 650.0, 50.0, "Koregaon Park Approach", "North-East"),
    ("CAM_PUN_008", "CAM_PUN_009", 1400.0, 100.0, 400.0, 50.0, "North Main to Kalyani Nagar", "North-East"),
    ("CAM_PUN_009", "CAM_PUN_010", 2800.0, 190.0, 700.0, 60.0, "Airport Expressway Corridor", "Northbound"),

    # Central to West Corridor (SB Road, SPPU, Aundh, Baner)
    ("CAM_PUN_001", "CAM_PUN_011", 2100.0, 140.0, 500.0, 50.0, "Senapati Bapat Arterial", "Westbound"),
    ("CAM_PUN_011", "CAM_PUN_012", 2200.0, 150.0, 520.0, 50.0, "SB Road to SPPU University Circle", "North-West"),
    ("CAM_PUN_012", "CAM_PUN_013", 2300.0, 155.0, 540.0, 50.0, "University to Aundh Corridor", "Westbound"),
    ("CAM_PUN_013", "CAM_PUN_014", 2400.0, 160.0, 550.0, 60.0, "Aundh to Baner High Street", "Westbound"),

    # South Corridor & Transits (Swargate)
    ("CAM_PUN_004", "CAM_PUN_015", 2500.0, 180.0, 700.0, 40.0, "Deccan to Swargate Transit Route", "Southbound"),
    ("CAM_PUN_015", "CAM_PUN_007", 3800.0, 260.0, 900.0, 50.0, "Swargate to Pune Station Link", "North-East"),

    # Western Return Corridor
    ("CAM_PUN_012", "CAM_PUN_001", 2800.0, 190.0, 650.0, 50.0, "Ganeshkhind Inbound to Shivaji Nagar", "South-East"),
]


async def seed_camera_network() -> dict:
    """
    Seeds the 15 simulated Pune cameras and 17 directed road connections into the database.
    Idempotent: updates existing or creates missing records without duplicates.
    """
    async with async_session_factory() as session:
        # 1. Clear existing road edges first (to satisfy FK constraints cleanly)
        await session.execute(delete(RoadEdge))
        await session.execute(delete(Camera))
        await session.flush()

        now = datetime.now(timezone.utc)
        cam_code_to_model = {}

        # 2. Insert Camera nodes
        for data in PUNE_CAMERAS:
            lat = data["latitude"]
            lon = data["longitude"]
            cam = Camera(
                camera_id=data["camera_id"],
                name=data["name"],
                description=data["description"],
                latitude=lat,
                longitude=lon,
                location=WKTElement(f"POINT({lon} {lat})", srid=4326),
                direction_angle=data["direction_angle"],
                road_name=data["road_name"],
                sector=data["sector"],
                status=data["status"],
                installation_metadata=data["installation_metadata"],
                created_at=now,
                updated_at=now
            )
            session.add(cam)
            cam_code_to_model[data["camera_id"]] = cam

        await session.flush()

        # 3. Insert Directed Road Edges
        edge_count = 0
        for src_code, dst_code, dist, min_time, max_time, speed, road, direction in ROAD_EDGES_CONFIG:
            src_cam = cam_code_to_model.get(src_code)
            dst_cam = cam_code_to_model.get(dst_code)
            if src_cam and dst_cam:
                edge = RoadEdge(
                    source_camera_id=src_cam.id,
                    destination_camera_id=dst_cam.id,
                    distance_meters=dist,
                    expected_min_travel_seconds=min_time,
                    expected_max_travel_seconds=max_time,
                    speed_limit_kmh=speed,
                    road_name=road,
                    direction=direction,
                    is_active=True,
                    created_at=now
                )
                session.add(edge)
                edge_count += 1

        await session.commit()

        return {
            "status": "success",
            "city": "Pune, Maharashtra, India",
            "cameras_seeded": len(PUNE_CAMERAS),
            "edges_seeded": edge_count
        }


if __name__ == "__main__":
    result = asyncio.run(seed_camera_network())
    print(f"Seed completed successfully: {result}")
