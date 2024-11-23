from services.recommendation.factors.recommendation_factor import RecommendationFactor, FactorStatus
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
                name="organic",
                findable_in = ["labels_tags"]
            ),
            RecommendationFactor(
                name="vegetarian",
                findable_in = ["labels_tags"]
            ),
            RecommendationFactor(
                name="eggs",
                findable_in = ["allergens", "traces_tags"],
            ),
            RecommendationFactor(
                name="milk",
                findable_in = ["allergens", "traces_tags"]
            ),
            RecommendationFactor(
                name="nuts",
                findable_in = ["allergens", "traces_tags"]
            )
        ]
        return cls(
            recommendation_factors=default_factors,
            nutritional_rating_system=Nutriscore()
        )
    
    def __post_init__(self):
        if not self.recommendation_factors:
            raise ValueError("At least one recommendation factor is required")