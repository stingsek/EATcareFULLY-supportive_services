from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class RecommendationFactor:
    """
    Immutable configuration for a single recommendation factor.
    
    Attributes:
        name: Factor name corresponding to DataFrame column
        weight: Factor importance weight
        content: List of values to match
        avoid: Whether to exclude products with matching content
        threshold: Optional threshold value for numerical comparisons
    """
    name: str
    weight: float
    content: List[str]
    avoid: bool = False
    threshold: Optional[float] = None

    def __post_init__(self):
        if self.weight <= 0:
            raise ValueError("Weight must be positive")
        if not self.content:
            raise ValueError("Content list cannot be empty")