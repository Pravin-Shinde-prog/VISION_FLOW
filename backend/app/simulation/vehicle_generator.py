import random
import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class SyntheticVehicle:
    vehicle_uid: str
    vehicle_type: str
    color: str
    make: str
    model: str
    window_tint: str
    visual_features: Dict[str, Any]
    normalized_plate: Optional[str]
    raw_plate_text: Optional[str]
    state_code: str
    plate_state: str  # NORMAL, PARTIAL, DAMAGED, OCCLUDED
    ocr_confidence: Optional[float]
    plate_anomaly_flags: Optional[Dict[str, Any]]


# Real-world vehicle models commonly seen in Pune / Indian urban traffic
VEHICLE_CATALOG = {
    "SUV": [
        ("Hyundai", "Creta"),
        ("Tata", "Nexon"),
        ("Mahindra", "Thar"),
        ("Toyota", "Fortuner"),
        ("Kia", "Seltos"),
        ("Mahindra", "Scorpio-N"),
    ],
    "sedan": [
        ("Honda", "City"),
        ("Hyundai", "Verna"),
        ("Maruti", "Dzire"),
        ("Skoda", "Slavia"),
        ("Volkswagen", "Virtus"),
    ],
    "hatchback": [
        ("Maruti", "Swift"),
        ("Hyundai", "i20"),
        ("Tata", "Altroz"),
        ("Maruti", "Baleno"),
        ("Tata", "Tiago"),
    ],
    "motorcycle": [
        ("Royal Enfield", "Classic 350"),
        ("Bajaj", "Pulsar NS200"),
        ("Hero", "Splendor Plus"),
        ("TVS", "Apache RTR 160"),
        ("Honda", "Shine"),
    ],
    "van": [
        ("Maruti", "Eeco"),
        ("Force", "Traveller"),
        ("Mahindra", "Bolero Maxi"),
    ],
    "truck": [
        ("Ashok Leyland", "Dost"),
        ("Tata", "Ace"),
        ("Eicher", "Pro 2049"),
        ("Tata", "407"),
    ],
}

COLORS = ["White", "Silver", "Black", "Grey", "Red", "Dark Blue", "Golden", "Brown", "Green"]
WINDOW_TINTS = ["none", "light", "medium", "dark"]
DISTINCTIVE_STICKERS = [
    "pune_municipal_pass",
    "society_parking_qr",
    "baby_on_board",
    "national_highway_fastag",
    "service_club_badge",
]


class VehicleGenerator:
    """Generates synthetic vehicle entities and plate records with controlled distributions."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self._generated_plates = set()

    def generate_fleet(self, count: int, config) -> List[SyntheticVehicle]:
        fleet: List[SyntheticVehicle] = []
        for idx in range(count):
            vehicle = self.generate_vehicle(idx, config)
            fleet.append(vehicle)
        return fleet

    def generate_vehicle(self, index: int, config) -> SyntheticVehicle:
        # Unique deterministic vehicle UID
        hex_suffix = "".join(self.rng.choices("0123456789abcdef", k=6))
        veh_uid = f"veh_sim_{self.rng.randint(100000, 999999)}_{hex_suffix}"

        # Vehicle type & Model selection
        v_type = self.rng.choice(list(VEHICLE_CATALOG.keys()))
        make, model = self.rng.choice(VEHICLE_CATALOG[v_type])
        color = self.rng.choice(COLORS)
        window_tint = self.rng.choice(WINDOW_TINTS)

        # Visual Features Metadata
        has_roof_rails = v_type in ["SUV", "van"] and self.rng.random() < 0.6
        stickers = self.rng.sample(DISTINCTIVE_STICKERS, k=self.rng.randint(0, 2))
        sig_hash = "".join(self.rng.choices("0123456789abcdef", k=16))
        visual_features = {
            "simulation": True,
            "data_source": "simulation",
            "city": "Pune",
            "roof_rails": has_roof_rails,
            "distinctive_features": stickers,
            "simulated_signature_hash": sig_hash,
        }

        # Plate readability distribution
        r = self.rng.random()
        if r < config.prob_normal:
            plate_state = "NORMAL"
        elif r < config.prob_normal + config.prob_partial:
            plate_state = "PARTIAL"
        elif r < config.prob_normal + config.prob_partial + config.prob_damaged:
            plate_state = "DAMAGED"
        else:
            plate_state = "OCCLUDED"

        # Generate Pune-style plate number (MH12 + AA..ZZ + 1000..9999)
        normalized_plate: Optional[str] = None
        raw_plate_text: Optional[str] = None
        ocr_confidence: Optional[float] = None
        anomaly_flags: Optional[Dict[str, Any]] = None

        if plate_state != "OCCLUDED":
            # Generate unique plate
            while True:
                letters = "".join(self.rng.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
                digits = f"{self.rng.randint(1000, 9999)}"
                candidate = f"MH12{letters}{digits}"
                if candidate not in self._generated_plates:
                    self._generated_plates.add(candidate)
                    normalized_plate = candidate
                    raw_plate_text = f"MH 12 {letters} {digits}"
                    break

            if plate_state == "NORMAL":
                ocr_confidence = round(self.rng.uniform(0.88, 0.99), 3)
                anomaly_flags = {"is_broken": False, "is_modified": False, "simulation": True}
            elif plate_state == "PARTIAL":
                ocr_confidence = round(self.rng.uniform(0.50, 0.78), 3)
                anomaly_flags = {"is_broken": False, "is_partially_obscured": True, "simulation": True}
            elif plate_state == "DAMAGED":
                ocr_confidence = round(self.rng.uniform(0.65, 0.85), 3)
                anomaly_flags = {
                    "is_broken": True,
                    "is_non_standard": self.rng.random() < 0.5,
                    "simulation": True,
                }
        else:
            # Occluded / missing plate
            normalized_plate = None
            raw_plate_text = None
            ocr_confidence = None
            anomaly_flags = {"is_missing": True, "is_occluded": True, "simulation": True}

        return SyntheticVehicle(
            vehicle_uid=veh_uid,
            vehicle_type=v_type,
            color=color,
            make=make,
            model=model,
            window_tint=window_tint,
            visual_features=visual_features,
            normalized_plate=normalized_plate,
            raw_plate_text=raw_plate_text,
            state_code="MH",
            plate_state=plate_state,
            ocr_confidence=ocr_confidence,
            plate_anomaly_flags=anomaly_flags,
        )
