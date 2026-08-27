from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class SimulationConfig:
    """
    Configuration parameters for synthetic traffic and camera-event simulation.
    All data produced is explicitly marked as simulated development data.
    """
    vehicle_count: int = 30
    events_per_vehicle: int = 5
    seed: Optional[int] = 42
    start_time: Optional[datetime] = None

    # Realistic physical travel time variations
    speed_variation_pct: float = 0.15  # +/- 15% variation around expected travel time
    delay_probability: float = 0.20    # 20% probability of traffic / intersection delay
    min_delay_seconds: float = 15.0
    max_delay_seconds: float = 90.0

    # Plate OCR readability probability distribution (sums to 1.0)
    prob_normal: float = 0.80    # Clean plate with high OCR confidence (0.88 - 0.99)
    prob_partial: float = 0.10   # Partially obscured plate with lower OCR confidence (0.50 - 0.78)
    prob_damaged: float = 0.05   # Broken/modified plate with compliance anomaly flags
    prob_occluded: float = 0.05  # Missing or completely occluded plate (null plate_number)

    def get_start_time(self) -> datetime:
        """Returns configured start_time or defaults to 1 hour ago UTC."""
        if self.start_time:
            return self.start_time if self.start_time.tzinfo else self.start_time.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - timedelta(hours=1)
