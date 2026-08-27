import re
from typing import List, Tuple, Optional
from app.anpr.schemas import PlateNormalizationResult
from app.anpr.validator import IndianPlateValidator

# Positional substitution maps for common optical character confusion
DIGIT_TO_LETTER = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "4": "A",
    "5": "S",
    "6": "G",
    "8": "B",
}

LETTER_TO_DIGIT = {
    "O": "0",
    "D": "0",
    "Q": "0",
    "I": "1",
    "L": "1",
    "T": "1",
    "Z": "2",
    "A": "4",
    "S": "5",
    "G": "6",
    "B": "8",
}


class IndianPlateNormalizer:
    """
    Normalizes raw OCR character text according to positional syntax rules of Indian license plates.
    Corrects optical confusions (e.g. 0 vs O, 1 vs I, 8 vs B, 5 vs S) based on index position.
    """

    def __init__(self):
        self.validator = IndianPlateValidator()

    def normalize(self, raw_text: str) -> PlateNormalizationResult:
        if not raw_text:
            return PlateNormalizationResult(
                raw_text="",
                normalized_plate=None,
                substitutions_made=[],
                is_normalized=False
            )

        # 1. Clean noise, spaces, hyphens, and punctuation
        cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
        if len(cleaned) < 5:
            return PlateNormalizationResult(
                raw_text=raw_text,
                normalized_plate=cleaned if len(cleaned) >= 5 else None,
                substitutions_made=[],
                is_normalized=False
            )

        # If already fully valid, return directly
        val_check = self.validator.validate(cleaned)
        if val_check.is_valid:
            return PlateNormalizationResult(
                raw_text=raw_text,
                normalized_plate=cleaned,
                substitutions_made=[],
                is_normalized=False
            )

        # 2. Positional normalization for standard 10-character plate: [AA][00][AA][0000]
        substitutions: List[str] = []
        normalized_chars = list(cleaned)

        # Standard 10-character layout
        if len(normalized_chars) == 10:
            # Pos 0-1: State Code (Must be Letters)
            for i in [0, 1]:
                c = normalized_chars[i]
                if c.isdigit() and c in DIGIT_TO_LETTER:
                    replacement = DIGIT_TO_LETTER[c]
                    substitutions.append(f"Pos {i}: '{c}' -> '{replacement}' (State letter)")
                    normalized_chars[i] = replacement

            # Pos 2-3: District Code (Must be Digits)
            for i in [2, 3]:
                c = normalized_chars[i]
                if c.isalpha() and c in LETTER_TO_DIGIT:
                    replacement = LETTER_TO_DIGIT[c]
                    substitutions.append(f"Pos {i}: '{c}' -> '{replacement}' (District digit)")
                    normalized_chars[i] = replacement

            # Pos 4-5: Series Code (Must be Letters)
            for i in [4, 5]:
                c = normalized_chars[i]
                if c.isdigit() and c in DIGIT_TO_LETTER:
                    replacement = DIGIT_TO_LETTER[c]
                    substitutions.append(f"Pos {i}: '{c}' -> '{replacement}' (Series letter)")
                    normalized_chars[i] = replacement

            # Pos 6-9: Serial Number (Must be Digits)
            for i in range(6, 10):
                c = normalized_chars[i]
                if c.isalpha() and c in LETTER_TO_DIGIT:
                    replacement = LETTER_TO_DIGIT[c]
                    substitutions.append(f"Pos {i}: '{c}' -> '{replacement}' (Number digit)")
                    normalized_chars[i] = replacement

        # Standard 9-character layout: [AA][00][A][0000]
        elif len(normalized_chars) == 9:
            # Pos 0-1: State
            for i in [0, 1]:
                if normalized_chars[i].isdigit() and normalized_chars[i] in DIGIT_TO_LETTER:
                    substitutions.append(f"Pos {i}: '{normalized_chars[i]}' -> '{DIGIT_TO_LETTER[normalized_chars[i]]}'")
                    normalized_chars[i] = DIGIT_TO_LETTER[normalized_chars[i]]
            # Pos 2-3: District
            for i in [2, 3]:
                if normalized_chars[i].isalpha() and normalized_chars[i] in LETTER_TO_DIGIT:
                    substitutions.append(f"Pos {i}: '{normalized_chars[i]}' -> '{LETTER_TO_DIGIT[normalized_chars[i]]}'")
                    normalized_chars[i] = LETTER_TO_DIGIT[normalized_chars[i]]
            # Pos 4: Single Series Letter
            if normalized_chars[4].isdigit() and normalized_chars[4] in DIGIT_TO_LETTER:
                substitutions.append(f"Pos 4: '{normalized_chars[4]}' -> '{DIGIT_TO_LETTER[normalized_chars[4]]}'")
                normalized_chars[4] = DIGIT_TO_LETTER[normalized_chars[4]]
            # Pos 5-8: Number Digits
            for i in range(5, 9):
                if normalized_chars[i].isalpha() and normalized_chars[i] in LETTER_TO_DIGIT:
                    substitutions.append(f"Pos {i}: '{normalized_chars[i]}' -> '{LETTER_TO_DIGIT[normalized_chars[i]]}'")
                    normalized_chars[i] = LETTER_TO_DIGIT[normalized_chars[i]]

        candidate_plate = "".join(normalized_chars)

        return PlateNormalizationResult(
            raw_text=raw_text,
            normalized_plate=candidate_plate,
            substitutions_made=substitutions,
            is_normalized=len(substitutions) > 0
        )
