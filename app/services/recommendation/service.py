from typing import List
from models.domain.off_product import OpenFoodFactsProduct
from app.models.schemas.product_recommendation import ProductRecommendationRequest, RecommendedProduct
from app.utils.dataset_manager import DatasetManager
from app.services.recommendation.engine import RecommendationEngine
from app.utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)


class RecommendationService:
    
    def __init__(self, dataset_manager: DatasetManager) -> None:
        self.dataset_manager = dataset_manager
        self.engine = RecommendationEngine()

    async def generate_recommendations(self, request: ProductRecommendationRequest) -> List[RecommendedProduct]:
            
            logger.info(f"Generating recommendations for product {request.product_code}")
            
            dataset = self.dataset_manager.get_dataset()
            logger.info(f"Got dataset")
            if dataset is None:
                raise Exception("Dataset not available")
            

            user_preferences = request.user_preferences
            logger.info(f"Got user prefs")
            
            product_details = dataset[dataset["code"].astype(str) == request.product_code].squeeze()
            
            dataset = dataset[dataset['code'].astype(str) != request.product_code]
            logger.info(f"Excluded source product from dataset")


            product = OpenFoodFactsProduct(request.product_code, product_details)
            logger.info(f"Got product")
            
            
            self.engine.recommendation_strategy.update_factors_status(user_preferences=user_preferences)
            logger.info(f"updated factors status")
            logger.info(f"Start finding recommendations")
            recommendations = self.engine.find_recommendations(dataset, product, request.limit)
            logger.info(f"Got recommendations")
            
            return recommendations

