from functools import lru_cache
from app.utils.dataset_manager import DatasetManager

@lru_cache(maxsize=1)
def get_dataset_manager():
    return DatasetManager("/app/data/processed/openfoodfacts.pkl")

