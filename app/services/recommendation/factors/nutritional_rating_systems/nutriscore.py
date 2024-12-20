from services.recommendation.factors.nutritional_rating_systems.nutritional_rating_system import NutritionalScore, NutritionalRatingSystem
from models.domain.off_product import OpenFoodFactsProduct
from services.recommendation.evaluator.off_evaluator import OpenFoodFactsProductEvaluator
from services.recommendation.factors.recommendation_factor import RecommendationFactor, FactorPreferenceStatus
from enum import Enum
from typing import List
from pandas import notna
from utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)


class NutriscoreGrade(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    
    def __lt__(self, other):
        grades_order = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        return grades_order[self.value] < grades_order[other.value]
        
    def __gt__(self, other):
        grades_order = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        return grades_order[self.value] > grades_order[other.value]
        
    def __le__(self, other):
        return self < other or self == other
        
    def __ge__(self, other):
        return self > other or self == other


class Nutriscore(NutritionalRatingSystem):
    """Implementation of the Nutri-Score rating system."""
    
    def __init__(self, maximize_score=False):
        super().__init__(maximize_score)
        self._thresholds = self._initialize_thresholds()
        
    @staticmethod
    def _initialize_thresholds() -> dict:
        """Initialize scoring thresholds for different product categories."""
        return {
            "energy": {
                "solid": [80, 160, 240, 320, 400, 480, 560, 640, 720, 800],
                "beverage": [7.2, 14.3, 21.5, 28.5, 35.9, 43.0, 50.2, 57.4, 64.5, float('inf')]
            },
            "sugar": {
                "solid": [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45],
                "beverage": [0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5]
            },
            "saturated_fat": {
                "cooking_fats": [10, 16, 22, 28, 34, 40, 46, 52, 58, 64],
                "default": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            },
            "sodium": [90, 180, 270, 360, 450, 540, 630, 720, 810, 900],
            "fiber": [0.7, 1.4, 2.1, 2.8, 3.5],
            "protein": [1.6, 3.2, 4.8, 6.4, 8.0]
        }


    def _score_based_on_thresholds(self, value: float, thresholds: list, max_score: int) -> int:
        """Calculate score based on value and thresholds."""
        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return i
        return max_score

    def calculate_score(self, product: OpenFoodFactsProduct) -> NutritionalScore:
        """
        Calculate Nutri-Score for a product.
        
        Args:
            product: OpenFoodFactsProduct instance
            
        Returns:
            NutritionalScore: Calculated Nutri-Score
        
        Raises:
            ValueError: If required nutritional data is missing
        """
        if product.details.empty:
            raise ValueError("No product details available")

        category = product.category.value
        
        # Calculate negative points
        logger.info(f"start negative points calculation for {product.code}")
        negative_points = sum([
            self._score_based_on_thresholds(
                product.details["energy_100g"],
                self._thresholds["energy"][category],
                10
            ),
            self._score_based_on_thresholds(
                product.details["sugars_100g"],
                self._thresholds["sugar"][category],
                10
            ),
            self._score_based_on_thresholds(
                product.details["saturated-fat_100g"],
                self._thresholds["saturated_fat"]["default"],
                10
            ),
            self._score_based_on_thresholds(
                product.details["salt_100g"],
                self._thresholds["sodium"],
                10
            )
        ])
        
        # Calculate positive points
        positive_points = sum([
            self._score_based_on_thresholds(
                product.details["fiber_100g"],
                self._thresholds["fiber"],
                5
            ),
            self._score_based_on_thresholds(
                product.details["proteins_100g"],
                self._thresholds["protein"],
                5
            )
        ])
        
        return NutritionalScore(negative_points - positive_points)

    def rate(self, product: OpenFoodFactsProduct) -> NutriscoreGrade:
        """
        Convert numerical score to Nutri-Score grade (A-E).
        
        Args:
            product: OpenFoodFactsProduct instance
            
        Returns:
            NutriscoreGrade: Nutri-Score grade (A-E)
        """
        score = self.calculate_score(product)
        category = product.category.value
        
        ranges = {
            "solid": {
                (-float('inf'), -1): NutriscoreGrade.A,
                (-1, 2): NutriscoreGrade.B,
                (2, 10): NutriscoreGrade.C,
                (10, 18): NutriscoreGrade.D,
                (18, float('inf')): NutriscoreGrade.E
            },
            "beverage": {
                (-float('inf'), 0): NutriscoreGrade.A,
                (0, 1): NutriscoreGrade.B,
                (1, 5): NutriscoreGrade.C,
                (5, 9): NutriscoreGrade.D,
                (9, float('inf')): NutriscoreGrade.E
            }
        }
        
        for (min_score, max_score), grade in ranges[category].items():
            if min_score < score <= max_score:
                return grade
            
        return NutriscoreGrade.E  # Default grade if no range matches
    
    def __has_nutriscore(self, product: OpenFoodFactsProduct) -> bool:
        return notna(product.details["nutriscore_grade"]) & (product.details["nutriscore_grade"] != "")
    
    def has_better_rating(self, product: OpenFoodFactsProduct, other: OpenFoodFactsProduct) -> bool:
        """
        Compare two products' Nutri-Score ratings.
        
        Args:
            product: First OpenFoodFactsProduct to compare
            other: Second OpenFoodFactsProduct to compare
                
        Returns:
            bool: True if first product has better (lower) Nutri-Score rating than the second one
            
        Raises:
            ValueError: If any of the products has empty details
        """
        
        if product.details.empty or other.details.empty:
            raise ValueError("Cannot compare empty products")
        
        def get_grade(prod: OpenFoodFactsProduct) -> NutriscoreGrade:
            if self.__has_nutriscore(prod):
                def convert_grade(grade_str):
                    return NutriscoreGrade[grade_str]
                logger.info(prod.details["nutriscore_grade"])
                return convert_grade(prod.details["nutriscore_grade"].upper())
            return self.rate(prod)
        
        logger.info(f"start comparing nutriscores for {product.code} and {other.code}")
        logger.info(f"start comparing nutriscores for {get_grade(product)} and {get_grade(other)}")
        logger.info(f"{get_grade(product) < get_grade(other)}")
        
        return get_grade(product) < get_grade(other)
    
class NutriscoreEvaluator(OpenFoodFactsProductEvaluator):
    """Evaluator for Nutri-Score based product scoring."""
    def __init__(self):
        super().__init__()
    
    def evaluate(self, product: OpenFoodFactsProduct, recommendation_factors: List[RecommendationFactor]) -> float:
        if product.details.empty:
            raise ValueError("Cannot evaluate empty product")
            
        if "nutriscore_score" not in product.details.index.tolist():
            raise ValueError("Product doesn't have nutriscore_score")
            
        score = float(product.details["nutriscore_score"])
        
        for factor in recommendation_factors:
            if factor.exists(product.details):
                    if factor.status == FactorPreferenceStatus.RECOMMEND:
                        score -= self.bonus
        return score
    
    