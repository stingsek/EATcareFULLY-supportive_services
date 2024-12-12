from typing import List
from models.domain.off_product import OpenFoodFactsProduct
from models.schemas.product_recommendation import ProductRecommendationRequest, RecommendedProduct
from utils.dataset_manager import DatasetManager
from services.recommendation.engine import RecommendationEngine
from utils.logger import setup_colored_logger
import math

logger = setup_colored_logger(__name__)


class RecommendationService:
    
    def __init__(self, dataset_manager: DatasetManager) -> None:
        self.dataset_manager = dataset_manager
        self.engine = RecommendationEngine()
        
    def __dataset(self):
        return self.dataset_manager.get_dataset()

    def __dataset_without_source_product(self, dataset, product_code):
        return dataset[dataset['code'].astype(str) != product_code]
    
    def __get_product_details(self, dataset, product_code):
        return dataset[dataset["code"].astype(str) == product_code].squeeze()
    
    def __sanitize_product_name(self, name_value):
        if not isinstance(name_value, str):
            logger.warning(f"Wrong datatype for name: {type(name_value)}")
        
        if name_value is None:
            return "Unknown name"
        
        if isinstance(name_value, float) and math.isnan(name_value):
            return "Unknown name"
            
        try:
            sanitized_name = str(name_value).strip()
            return sanitized_name if sanitized_name else "Unknown name"
        except Exception as e:
            logger.error(f"Error during name sanitization: {e}")
            return "Unknown"
    
    async def generate_recommendations(self, request: ProductRecommendationRequest) -> List[RecommendedProduct]:
            product_code = request.product_code
            user_preferences = request.user_preferences
            
            logger.info(f"Generating recommendations for product {product_code}")
            
            dataset = self.__dataset()
            if dataset is None:
                raise Exception("Dataset not available")
            
            logger.info(f"Got dataset")
            
            product_details = self.__get_product_details(dataset, product_code)
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
            
            recommendations_processed = []
            
            for recommendation_code in recommendations:
                product_details = self.__get_product_details(dataset, recommendation_code)
                product_name = self.__sanitize_product_name(product_details['product_name'])
                image_url = product_details['image_url']
                nutriscore = product_details['nutriscore_grade'].upper()
                recommendations_processed.append(RecommendedProduct(code=recommendation_code, name=product_name, image_url=image_url, nutriscore=nutriscore))
                
            return recommendations_processed

