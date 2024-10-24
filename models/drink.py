from dataclasses import dataclass, field
from typing import List

# Constants for validation
MIN_ALCOHOL: float = 0.0
MAX_ALCOHOL: float = 100.0
MIN_VOLUME: float = 0.0
MAX_VOLUME: float = 50.0
VALID_UNITS: List[str] = ["L", "ml", "cl"]


# Function to calculate volume in liters
def calculate_volume_in_liters(volume: float, unit: str) -> float:
    """Converts volume to liters based on the unit."""
    if unit == "L":
        return volume
    elif unit == "cl":
        return volume / 100
    elif unit == "ml":
        return volume / 1000
    else:
        raise ValueError(f"Invalid unit: {unit}. Must be one of {VALID_UNITS}.")


@dataclass
class Drink:
    name: str  # Name of the drink
    volume: float = field(default=0.5)  # Volume of the drink, default 0.5
    unit: str = field(default=VALID_UNITS[0])  # Unit of volume, default is "L"
    alcohol: float = field(default=MIN_ALCOHOL)  # Alcohol percentage, default is 0.0

    def __post_init__(self) -> None:
        """Validates and initializes the drink properties."""
        # Validate the unit
        if self.unit not in VALID_UNITS:
            raise ValueError(f"Unit must be one of {VALID_UNITS}, got '{self.unit}'")

        # Validate alcohol percentage
        if not (MIN_ALCOHOL <= self.alcohol <= MAX_ALCOHOL):
            raise ValueError(
                f"Alcohol percentage must be between {MIN_ALCOHOL} and {MAX_ALCOHOL}, got {self.alcohol}"
            )

        # Validate volume
        if not (MIN_VOLUME <= self.volume_in_liters() <= MAX_VOLUME):
            raise ValueError(
                f"Volume must be between {MIN_VOLUME} and {MAX_VOLUME} liters, got {self.volume_in_liters()}"
            )

        # Ensure the name starts with an uppercase letter
        if not self.name[0].isupper():
            raise ValueError("Drink name must start with an uppercase letter")

    def volume_in_liters(self) -> float:
        """Converts and returns the volume of the drink in liters."""
        result = calculate_volume_in_liters(self.volume, self.unit)

        if result < 0.0:
            raise ValueError("Volume in liters cannot be negative")

        # Convert the volume and update the unit based on the original unit.
        if self.unit == "ml" and result > 1.0:
            self.volume = round(self.volume / 1000, 2)
            self.unit = "L"
        elif self.unit == "cl" and result > 1.0:
            self.volume = round(self.volume / 100, 2)
            self.unit = "L"

        return result

    def alcohol_content(self) -> float:
        """Calculates the alcohol content in liters."""
        return round(self.volume_in_liters() * (self.alcohol / 100), 2)

    def __str__(self) -> str:
        """Provides a user-friendly string representation of the drink."""
        return f"{self.name} ({self.volume} {self.unit}, {self.alcohol}%)"

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the drink."""
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        """Compares two drinks for equality based on their name and unit."""
        if not isinstance(other, Drink):
            return NotImplemented
        return (
            self.name.lower() == other.name.lower()
            and self.unit.lower() == other.unit.lower()
            and self.alcohol == other.alcohol
            and self.volume == other.volume
        )

    def __hash__(self):
        return hash((self.name, self.volume, self.alcohol))
