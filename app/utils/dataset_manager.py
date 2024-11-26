from typing import Any, Optional
from pathlib import Path
import logging
import os
import pickle
import shutil
from functools import lru_cache
from app.utils.large_dataset_cache import LargeDatasetCache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_cache_instance() -> LargeDatasetCache:
    return LargeDatasetCache(max_memory_percent=75.0)

class DatasetManager:
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.temp_path = Path("/tmp/openfoodfacts.pkl")
        self.cache = get_cache_instance()
        
    def initialize_dataset(self):
        """Initialize dataset at container startup"""
        try:
            if not self.dataset_path.exists():
                logger.info("Dataset not found in volume, copying from image...")
                self._copy_dataset_to_volume()
            
            # Verify dataset
            self._verify_dataset()
            
            # Preload to cache
            self.get_dataset()
            
            logger.info("Dataset initialized and cached successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dataset: {e}")
            raise
            
    def _copy_dataset_to_volume(self):
        """Copy dataset from image to volume"""
        os.makedirs(self.dataset_path.parent, exist_ok=True)
        shutil.copy2(self.temp_path, self.dataset_path)
        
    def _verify_dataset(self):
        """Verify dataset integrity"""
        try:
            with open(self.dataset_path, 'rb') as f:
                pickle.load(f)
        except Exception as e:
            logger.error(f"Dataset verification failed: {e}")
            raise
            
    def get_dataset(self, default: Any = None) -> Optional[Any]:
        """
        Get dataset from cache or load it if needed
        
        Args:
            default: Default value to return in case of error
            
        Returns:
            Dataset or default value
        """
        try:
            if not self.dataset_path.exists():
                logger.error("Dataset file not found")
                return default
                
            dataset = self.cache.get(str(self.dataset_path))
            
            if dataset is None:
                logger.warning("Failed to get dataset from cache")
                return default
                
            return dataset
            
        except Exception as e:
            logger.exception(f"Error getting dataset: {e}")
            return default
            
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        
        
    def health_check(self) -> dict:
        """
        Check health status of dataset and cache
        Returns:
            dict: Health status information
        """
        try:
            dataset_exists = self.dataset_path.exists()
            cache_stats = self.cache.get_stats()
            dataset = self.get_dataset()
            
            return {
                "status": "healthy" if all([dataset_exists, dataset is not None]) else "unhealthy",
                "details": {
                    "dataset_available": dataset_exists,
                    "dataset_loaded": dataset is not None,
                    "cache_usage": f"{cache_stats['memory_percent']:.2f}%",
                    "cached_files": cache_stats['cached_files'],
                    "dataset_path": str(self.dataset_path)
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
