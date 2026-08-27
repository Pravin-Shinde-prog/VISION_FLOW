import re
from typing import Optional, Set
from app.anpr.schemas import PlateComponents, PlateValidationResult

# Recognized Indian State and Union Territory RTO Codes
VALID_INDIAN_STATES: Set[str] = {
    "MH",  # Maharashtra
    "DL",  # Delhi
    "KA",  # Karnataka
    "TN",  # Tamil Nadu
    "GJ",  # Gujarat
    "UP",  # Uttar Pradesh
    "HR",  # Haryana
    "TS",  # Telangana
    "AP",  # Andhra Pradesh
    "RJ",  # Rajasthan
    "MP",  # Madhya Pradesh
    "WB",  # West Bengal
    "KL",  # Kerala
    "PB",  # Punjab
    "CH",  # Chandigarh
    "GA",  # Goa
    "OD",  # Odisha
    "OR",  # Odisha (legacy)
    "JH",  # Jharkhand
    "BR",  # Bihar
    "UK",  # Uttarakhand
    "UA",  # Uttarakhand (legacy)
    "HP",  # Himachal Pradesh
    "AS",  # Assam
    "TR",  # Tripura
    "ML",  # Meghalaya
    "MN",  # Manipur
    "NL",  # Nagaland
    "MZ",  # Mizoram
    "SK",  # Sikkim
    "AR",  # Arunachal Pradesh
    "PY",  # Puducherry
    "DN",  # Dadra & Nagar Haveli
    "DD",  # Daman & Diu
    "AN",  # Andaman & Nicobar
    "LD",  # Lakshadweep
    "LA",  # Ladakh
    "JK",  # Jammu & Kashmir
}

# Regular expression patterns for Indian registration formats
STANDARD_HSRP_REGEX = re.compile(r"^([A-Z]{2})([0-9]{2})([A-Z]{1,3})([0-9]{4})$")
BHARAT_SERIES_REGEX = re.compile(r"^([0-9]{2})(BH)([0-9]{4})([A-Z]{1,2})$")
LEGACY_COMMERCIAL_REGEX = re.compile(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{1,2})([0-9]{1,4})$")


class IndianPlateValidator:
    """
    Validates license plate strings against official Indian Motor Vehicle registration standards.
    Supports Standard HSRP, Bharat (BH) series, and Legacy commercial patterns.
    """

    def validate(self, plate_str: Optional[str]) -> PlateValidationResult:
        if not plate_str:
            return PlateValidationResult(
                is_valid=False,
                format_type="invalid",
                components=None,
                validation_message="Plate string is empty or null.",
                confidence_penalty=0.40,
            )

        clean = plate_str.strip().upper().replace(" ", "").replace("-", "").replace(".", "")

        # 1. Standard Indian HSRP Format (e.g. MH12AB1234, DL01C9999)
        m_hsrp = STANDARD_HSRP_REGEX.match(clean)
        if m_hsrp:
            state, district, series, num = m_hsrp.groups()
            is_state_valid = state in VALID_INDIAN_STATES
            components = PlateComponents(
                state_code=state,
                district_code=district,
                series=series,
                registration_number=num,
            )

            if is_state_valid:
                return PlateValidationResult(
                    is_valid=True,
                    format_type="standard_hsrp",
                    components=components,
                    validation_message=f"Valid standard HSRP plate for state {state}, district {district}.",
                    confidence_penalty=0.0,
                )
            else:
                return PlateValidationResult(
                    is_valid=False,
                    format_type="standard_hsrp",
                    components=components,
                    validation_message=f"State code '{state}' is not a recognized Indian State/UT code.",
                    confidence_penalty=0.20,
                )

        # 2. Bharat Series Format (e.g. 22BH1234AA)
        m_bh = BHARAT_SERIES_REGEX.match(clean)
        if m_bh:
            year, bh, num, series = m_bh.groups()
            components = PlateComponents(
                state_code=bh,
                district_code=year,
                series=series,
                registration_number=num,
            )
            return PlateValidationResult(
                is_valid=True,
                format_type="bharat_series",
                components=components,
                validation_message=f"Valid Bharat (BH) series plate registered in 20{year}.",
                confidence_penalty=0.0,
            )

        # 3. Legacy / 2-Wheeler / Commercial Variations (e.g. MH12A123, DL1C1234)
        m_leg = LEGACY_COMMERCIAL_REGEX.match(clean)
        if m_leg:
            state, district, series, num = m_leg.groups()
            is_state_valid = state in VALID_INDIAN_STATES
            components = PlateComponents(
                state_code=state,
                district_code=district.zfill(2),
                series=series,
                registration_number=num.zfill(4),
            )
            return PlateValidationResult(
                is_valid=is_state_valid,
                format_type="legacy_commercial",
                components=components,
                validation_message=f"Legacy / Variable length Indian plate ({state} district {district}).",
                confidence_penalty=0.05 if is_state_valid else 0.25,
            )

        return PlateValidationResult(
            is_valid=False,
            format_type="invalid",
            components=None,
            validation_message=f"Text '{clean}' does not match any recognized Indian plate format.",
            confidence_penalty=0.35,
        )
