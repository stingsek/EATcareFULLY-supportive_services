from abc import ABC, abstractmethod
from typing import Any
from models.domain.off_product import OpenFoodFactsProduct

class NutritionalScore:
    """Value object representing a nutritional score."""
    def __init__(self, value: float):
        self._value = value
    
    @property
    def value(self) -> float:
        return self._value
    
    def __lt__(self, other: 'NutritionalScore') -> bool:
        return self._value < other._value
    
    
class NutritionalRatingSystem(ABC):
    """Abstract base class for nutritional rating systems."""
def __init__(self, maximize_score: bool = False):
    self.maximize_score = maximize_score

@abstractmethod
def calculate_score(self, product: OpenFoodFactsProduct) -> NutritionalScore:
    """Calculate nutritional score for a product."""
    pass

@abstractmethod
def rate(self, product: OpenFoodFactsProduct) -> Any:
    """Convert numerical score to specific grade."""
    pass