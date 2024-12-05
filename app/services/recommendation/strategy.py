from services.recommendation.factors.recommendation_factor import RecommendationFactor
from dataclasses import dataclass
from models.schemas.product_recommendation import UserPreference
from typing import List, Optional
from services.recommendation.factors.nutritional_rating_systems.nutriscore import Nutriscore
from services.recommendation.factors.nutritional_rating_systems.nutritional_rating_system import NutritionalRatingSystem
from utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)

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
    
    def update_factors_status(self, user_preferences: Optional[List[UserPreference]] = None) -> None:
        logger.info("Updating factors status")
        if not user_preferences:
            logger.warning("No user preferences provided")
            return
        
        for user_preference in user_preferences:
            preference_name = user_preference.name
            status = user_preference.status
            if factor := self.__factors_dict.get(preference_name):
                factor.update_status(status)
                            
    
    def __post_init__(self):
        if not self.recommendation_factors:
            raise ValueError("At least one recommendation factor is required")
        self.__factors_dict = {factor.name: factor for factor in self.recommendation_factors}