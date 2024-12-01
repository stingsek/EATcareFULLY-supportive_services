from functools import lru_cache
from app.utils.dataset_manager import DatasetManager
from app.services.recommendation.service import RecommendationService

@lru_cache(maxsize=1)
def get_dataset_manager():
    return DatasetManager(dataset_path=r"../data2/")

@lru_cache(maxsize=1)
def get_recommendation_service():
    return RecommendationService(get_dataset_manager())