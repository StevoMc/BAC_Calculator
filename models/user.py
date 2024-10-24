from dataclasses import dataclass, field
from typing import Literal

# Constants for validation
MIN_AGE: int = 0
MAX_AGE: int = 150
MIN_WEIGHT: float = 0.0
MAX_WEIGHT: float = 500.0

@dataclass
class User:
    name: str                            # User's name
    age: int = field(default=18)          # User's age, default is 18
    gender: Literal["male", "female"] = field(default="male")  # Gender as "male" or "female", default "male"
    weight: float = field(default=70.0)  
    
    def __post_init__(self) -> None:
        """Validates and initializes user properties."""
        # Validate age
        if not (MIN_AGE <= self.age <= MAX_AGE):
            raise ValueError(f"Age must be between {MIN_AGE} and {MAX_AGE}, got {self.age}")
        
        # Validate weight
        if not (MIN_WEIGHT <= self.weight <= MAX_WEIGHT):
            raise ValueError(f"Weight must be between {MIN_WEIGHT} and {MAX_WEIGHT}, got {self.weight}")
    
    def __str__(self) -> str:
        """Provides a user-friendly string representation of the user."""
        return f"{self.name} ({self.age} years, {self.gender}, {self.weight} Kg)"
    
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation of the user."""
        return self.__str__()
    
    def __eq__(self, other: object) -> bool:
        """Compares two users for equality based on their attributes."""
        if not isinstance(other, User):
            return NotImplemented
        return (
            self.name == other.name and
            self.age == other.age and
            self.gender == other.gender and
            self.weight == other.weight
        )
