import math
from datetime import datetime
from typing import Optional, Tuple


class SpatialTemporalValidator:
    """
    Computes spatial geodesic distance and temporal kinematics between camera observations.
    Validates whether two observations are physically and temporally plausible.
    """

    @staticmethod
    def haversine_distance_meters(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Computes great-circle distance between two GPS coordinates in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2 +
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 1)

    @classmethod
    def evaluate(
        cls,
        time_a: Optional[datetime],
        time_b: Optional[datetime],
        lat_a: Optional[float],
        lon_a: Optional[float],
        lat_b: Optional[float],
        lon_b: Optional[float]
    ) -> Tuple[Optional[float], Optional[float], Optional[float], bool]:
        """
        Returns (delta_time_seconds, distance_meters, speed_kmh, is_temporally_plausible)
        """
        delta_time: Optional[float] = None
        dist_m: Optional[float] = None
        speed_kmh: Optional[float] = None
        is_plausible = True

        if time_a and time_b:
            delta_time = abs((time_b - time_a).total_seconds())

        if lat_a is not None and lon_a is not None and lat_b is not None and lon_b is not None:
            dist_m = cls.haversine_distance_meters(lat_a, lon_a, lat_b, lon_b)

        if delta_time is not None and dist_m is not None:
            if delta_time > 0:
                # Speed in km/h = (distance / time) * 3.6
                speed_kmh = round((dist_m / delta_time) * 3.6, 1)
                # Max plausible urban corridor velocity is ~150 km/h
                if speed_kmh > 150.0 and dist_m > 300.0:
                    is_plausible = False
            else:
                # Same second across distant cameras (>100m) is impossible for same physical vehicle
                if dist_m > 100.0:
                    is_plausible = False

        return delta_time, dist_m, speed_kmh, is_plausible
