from services.recommendation.factors.recommendation_factor import RecommendationFactor
from dataclasses import dataclass
from typing import List
from services.recommendation.factors.nutritional_rating_systems.nutriscore import Nutriscore
from services.recommendation.factors.nutritional_rating_systems.nutritional_rating_system import NutritionalRatingSystem

@dataclass
class RecommendationStrategy:
    """
    Configuration for product recommendations.
    
    Attributes:
        recommendation_factors: List of recommendation factors
        nutritional_rating_system: System for nutritional scoring
    """
    recommendation_factors: List[RecommendationFactor]
    nutritional_rating_system: 'NutritionalRatingSystem'
    
    @classmethod
    def create_default(cls) -> "RecommendationStrategy":
        default_factors = [
            RecommendationFactor(
                name="labels_en",
                weight=1,
                content=["No alcohol", "No colorings"]
            ),
            RecommendationFactor(
                name="traces_tags",
                weight=1,
                content=["nuts"],
                avoid=True
            ),
            RecommendationFactor(
                name="allergens",
                weight=1,
                content=["gluten"],
                avoid=True
            )
        ]
        return cls(
            recommendation_factors=default_factors,
            nutritional_rating_system=Nutriscore()
        )
    
    def __post_init__(self):
        if not self.recommendation_factors:
            raise ValueError("At least one recommendation factor is required")