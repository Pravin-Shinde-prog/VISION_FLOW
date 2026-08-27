from typing import Dict
from sqlalchemy import text
from app.db.session import async_session_factory


async def cleanup_simulation_data() -> Dict[str, int]:
    """
    Safely deletes all records created by the simulation engine.
    Targets only records with simulation metadata or simulated snapshot paths.
    Does NOT affect cameras, road edges, or non-simulation entities.
    """
    async with async_session_factory() as session:
        # 1. Delete simulated detections
        del_det = await session.execute(
            text("""
                DELETE FROM detections
                WHERE snapshot_path LIKE 'simulated://%'
                   OR processing_metadata->>'simulation' = 'true'
                   OR plate_anomaly_flags->>'simulation' = 'true';
            """)
        )
        detections_count = del_det.rowcount

        # 2. Delete simulated vehicle plates
        del_plates = await session.execute(
            text("""
                DELETE FROM vehicle_plates
                WHERE anomaly_flags->>'simulation' = 'true';
            """)
        )
        plates_count = del_plates.rowcount

        # 3. Delete simulated vehicles
        del_veh = await session.execute(
            text("""
                DELETE FROM vehicles
                WHERE visual_features->>'simulation' = 'true'
                   OR vehicle_uid LIKE 'veh_sim_%';
            """)
        )
        vehicles_count = del_veh.rowcount

        await session.commit()

        return {
            "detections_deleted": detections_count,
            "plates_deleted": plates_count,
            "vehicles_deleted": vehicles_count,
        }
