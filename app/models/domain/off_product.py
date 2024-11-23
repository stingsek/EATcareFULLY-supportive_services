from dataclasses import dataclass, field
import pandas as pd
from enum import Enum
from typing import Any, List

class ProductCategory(Enum):
    SOLID = "solid"
    BEVERAGE = "beverage"
    COOKING_FATS = "cooking_fats"
    
@dataclass(frozen=True)
class OpenFoodFactsProduct:
    """
    Immutable representation of a product from OpenFoodFacts database.
    
    Attributes:
        code: Product unique identifier
        details: Product details as DataFrame row
    """
    code: str
    details: pd.Series
    
    @property
    def category(self) -> ProductCategory:
        """Returns the main category of the product."""
        if not self.details.empty:
            if "beverages" in self.details.get("categories_en", "").lower():
                return ProductCategory.BEVERAGE
            return ProductCategory.SOLID
        raise ValueError(f"No product found with code {self.code}")
    
    
@dataclass
class OpenFoodFactsProductColumn:
        name: str
        is_numeric: bool = False
        correct_values: List[Any] = field(default_factory=list)
        accept_empty: bool = False