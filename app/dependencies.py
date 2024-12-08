from functools import lru_cache
from utils.dataset_manager import DatasetManager
from services.recommendation.service import RecommendationService

@lru_cache(maxsize=1)
def get_dataset_manager():
    return DatasetManager(dataset_file_name="openfoodfacts_sample.pkl")

@lru_cache(maxsize=1)
def get_recommendation_service():
    return RecommendationService(get_dataset_manager())