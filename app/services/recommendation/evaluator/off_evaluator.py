from abc import ABC, abstractmethod
from models.domain.off_product import OpenFoodFactsProduct
from app.services.recommendation.strategy import RecommendationStrategy
from typing import Optional

class OpenFoodFactsProductEvaluator(ABC):
    def __init__(self, bonus: Optional[int] = 5) -> None:
        super().__init__()
        self.bonus = bonus
        
    @abstractmethod
    def evaluate(self, product: OpenFoodFactsProduct, recommendation_strategy: RecommendationStrategy) -> float:
        pass