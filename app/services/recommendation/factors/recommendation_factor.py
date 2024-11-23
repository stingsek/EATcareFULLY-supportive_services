from dataclasses import field
from typing import List
from enum import Enum
import re
import pandas as pd


class FactorStatus(Enum):
    AVOID = -1
    NEUTRAL = 0
    RECOMMEND = 1

    
class RecommendationFactor:
    """
    Configuration for a single recommendation factor.
    
    Attributes:
        name: Factor name
        status: Factor acceptance status
        findable_in: column names from OpenFoodFacts product dataset where this factor can be found
    """
    name: str
    status: FactorStatus = FactorStatus.NEUTRAL
    findable_in: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.findable_in:
            raise ValueError("Column list cannot be empty")
        
    def exists(self, product_details: pd.Series) -> bool:
        """
        Check if factor is present in product details.
        
        Args:
            product_details: pd.Series containing product details
            
        Returns:
            bool: True if factor is present, False otherwise
        """
        if product_details.empty:
            return False
        
        for column in self.findable_in:
            if column not in product_details.columns:
                raise ValueError(f"column {column} not found in product details")
            if self.__occurs_in(product_details[column].iloc[0]):
                return True 
        return False
    
    def __str__(self):
        return self.name
    
    def __occurs_in(self, all_factors: str) -> bool:
        pattern = rf'(?:^|,)en:{self.name}(?:,|$)'
        return bool(re.search(pattern, all_factors))