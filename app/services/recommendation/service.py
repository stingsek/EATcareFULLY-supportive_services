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
        
    def __dataset(self):
        return self.dataset_manager.get_dataset()

    def __dataset_without_source_product(self, dataset, product_code):
        return dataset[dataset['code'].astype(str) != product_code]
    
    def __product_details(self, dataset, product_code):
        return dataset[dataset["code"].astype(str) == product_code].squeeze()
        
    async def generate_recommendations(self, request: ProductRecommendationRequest) -> List[RecommendedProduct]:
            product_code = request.product_code
            user_preferences = request.user_preferences
            
            logger.info(f"Generating recommendations for product {product_code}")
            
            dataset = self.__dataset()
            if dataset is None:
                raise Exception("Dataset not available")
            
            logger.info(f"Got dataset")
            
            product_details = self.__product_details(dataset, product_code)
            logger.info(f"Got source product details")
            
            product = OpenFoodFactsProduct(product_code, product_details)
            logger.info(f"Got product")
            
            dataset = self.__dataset_without_source_product(dataset, product_code)
            logger.info(f"Excluded source product from dataset")


            self.engine.recommendation_strategy.update_factors_status(user_preferences=user_preferences)
            logger.info(f"updated factors status")
            
            logger.info(f"Start finding recommendations")
            recommendations = self.engine.find_recommendations(dataset, product, request.limit)
            logger.info(f"Got recommendations")
            
            return recommendations

