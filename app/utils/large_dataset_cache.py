from functools import lru_cache
import pickle
from pathlib import Path
import sys
import psutil
import os
from typing import Optional, Any
import logging

class LargeDatasetCache:
    def __init__(self, max_memory_percent: float = 75.0):
        """
        Args:
            max_memory_percent: Maximum memory usage for the cache in percent of total system memory.
        """
        self._cache = {}
        self._memory_usage = {}
        self._max_memory = psutil.virtual_memory().total * (max_memory_percent / 100)
        self.logger = logging.getLogger(__name__)
    
    def _get_object_size(self, obj: Any) -> int:
        """Assess the size of an object in bytes"""
        return sys.getsizeof(obj)
    
    def _check_memory(self, size: int) -> bool:
        """Check if there is enough memory to store the object"""
        current_usage = sum(self._memory_usage.values())
        return (current_usage + size) <= self._max_memory
    
    def _free_memory(self, needed_size: int):
        """Free memory by removing large objects from the cache"""
        current_usage = sum(self._memory_usage.values())
        if current_usage + needed_size > self._max_memory:
            # sort files by size
            sorted_files = sorted(
                self._memory_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for filepath, size in sorted_files:
                self._cache.pop(filepath, None)
                self._memory_usage.pop(filepath, None)
                current_usage -= size
                
                if current_usage + needed_size <= self._max_memory:
                    break
    
    def get(self, filepath: str, default: Any = None) -> Optional[Any]:
        """
        Load a dataset from cache or file.
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return default
            
            # if file is already in cache, return it
            if filepath in self._cache:
                return self._cache[filepath]
            
            # load file and check size
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            size = self._get_object_size(data)
            
            # if dataset is too large, don't cache it
            if size > self._max_memory:
                self.logger.warning(
                    f"Dataset {filepath} is too large ({size} bytes) to cache. "
                    f"Max memory limit is {self._max_memory} bytes"
                )
                return data
            
            # Zwolnij pamięć jeśli potrzeba
            self._free_memory(size)
            
            # Dodaj do cache
            self._cache[filepath] = data
            self._memory_usage[filepath] = size
            
            self.logger.info(
                f"Cached {filepath}, size: {size} bytes, "
                f"total cache usage: {sum(self._memory_usage.values())} bytes"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {filepath}: {e}")
            return default
    
    def clear(self):
        """Clear the cache"""
        self._cache.clear()
        self._memory_usage.clear()
    
    def remove(self, filepath: str):
        """Remove a file from cache"""
        self._cache.pop(filepath, None)
        self._memory_usage.pop(filepath, None)
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'cached_files': len(self._cache),
            'total_usage': sum(self._memory_usage.values()),
            'max_memory': self._max_memory,
            'memory_percent': (sum(self._memory_usage.values()) / self._max_memory) * 100
        }

# Przykład użycia:
cache = LargeDatasetCache(max_memory_percent=75.0)

def get_dataset(filepath: str) -> Any:
    return cache.get(filepath)