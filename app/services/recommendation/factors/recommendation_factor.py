from dataclasses import field, dataclass
from typing import List
from enum import IntEnum
import re
import pandas as pd
from utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)

class FactorPreferenceStatus(IntEnum):
    AVOID = -1
    NEUTRAL = 0
    RECOMMEND = 1

@dataclass
class RecommendationFactor:
    """
    Configuration for a single recommendation factor.
    
    Attributes:
        name: Factor name
        status: Factor acceptance status
        findable_in: column names from OpenFoodFacts product dataset where this factor can be found
    """
    name: str
    status: FactorPreferenceStatus = FactorPreferenceStatus.NEUTRAL
    findable_in: List[str] = field(default_factory=list)
    

    def __post_init__(self):
        if not self.findable_in:
            raise ValueError("Column list cannot be empty")
        
        
    def update_status(self, new_status: FactorPreferenceStatus) -> None:
        """
        Update factor status.
        
        Args:
            new_status: new status to be set
        """
        self.status = new_status
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
            if pd.notna(product_details[column]):
                if column not in product_details.index.tolist():
                    raise ValueError(f"column {column} not found in product details")
                if self.__occurs_in(product_details[column]):
                    return True 
        return False
    
    def __str__(self) -> str:
        return f"{self.name} ({self.status.name})"
    
    def __repr__(self) -> str:
        return f"RecommendationFactor(name='{self.name}', status={self.status}, findable_in={self.findable_in})"
    
    def __occurs_in(self, all_factors: str) -> bool:
        pattern = rf'(?:^|,)en:{self.name}(?:,|$)'
        return bool(re.search(pattern, all_factors))