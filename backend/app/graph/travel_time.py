from typing import Tuple, Optional


class TravelTimeModel:
    """
    Calculates physical travel time boundaries, average speed, and speed ratio constraints.
    """

    @classmethod
    def evaluate_kinematics(
        cls,
        path_distance_meters: float,
        observed_delta_seconds: float,
        minimum_time_seconds: float,
        maximum_time_seconds: float,
        speed_limit_kmh: float
    ) -> Tuple[float, float]:
        """
        Returns (required_average_speed_kmh, speed_ratio)
        """
        if observed_delta_seconds <= 0:
            return 999.9, 99.9

        # Speed in km/h = (distance_km) / (time_hours)
        dist_km = path_distance_meters / 1000.0
        time_hours = observed_delta_seconds / 3600.0
        req_speed_kmh = round(dist_km / time_hours, 1)

        limit = max(10.0, speed_limit_kmh)
        speed_ratio = round(req_speed_kmh / limit, 2)

        return req_speed_kmh, speed_ratio
