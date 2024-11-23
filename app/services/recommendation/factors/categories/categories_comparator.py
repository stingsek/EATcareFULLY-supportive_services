from abc import ABC, abstractmethod

class CategoriesComparator(ABC):
    @abstractmethod
    def compare(self, product_categories: str, user_categories: str) -> float:
        pass
    
    