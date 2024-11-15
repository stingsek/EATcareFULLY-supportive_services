from abc import ABC, abstractmethod
from models.domain.off_product import OpenFoodFactsProduct
from services.recommendation.recommendation_strategy import RecommendationStrategy

class OpenFoodFactsProductEvaluator(ABC):
    @abstractmethod
    def evaluate(self, product: OpenFoodFactsProduct, recommendation_strategy: RecommendationStrategy) -> float:
        pass