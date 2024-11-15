from services.recommendation.factors.nutritional_rating_systems.nutritional_rating_system import NutritionalScore, NutritionalRatingSystem
from models.domain.off_product import OpenFoodFactsProduct
from services.recommendation.evaluator.off_evaluator import OpenFoodFactsProductEvaluator
from services.recommendation.recommendation_strategy import RecommendationStrategy

class Nutriscore(NutritionalRatingSystem):
    """Implementation of the Nutri-Score rating system."""
    
    def __init__(self, maximize_score: bool = False):
        
        super().__init__(maximize_score=maximize_score)
        
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
            float: Calculated Nutri-Score
        
        Raises:
            ValueError: If required nutritional data is missing
        """
        if product.details.empty:
            raise ValueError("No product details available")

        category = product.category.value
        
        # Calculate negative points
        negative_points = sum([
            self._score_based_on_thresholds(
                product.details["energy_100g"].iloc[0],
                self._thresholds["energy"][category],
                10
            ),
            self._score_based_on_thresholds(
                product.details["sugars_100g"].iloc[0],
                self._thresholds["sugar"][category],
                10
            ),
            self._score_based_on_thresholds(
                product.details["saturated-fat_100g"].iloc[0],
                self._thresholds["saturated_fat"]["default"],
                10
            ),
            self._score_based_on_thresholds(
                product.details["salt_100g"].iloc[0],
                self._thresholds["sodium"],
                10
            )
        ])
        
        # Calculate positive points
        positive_points = sum([
            self._score_based_on_thresholds(
                product.details["fiber_100g"].iloc[0],
                self._thresholds["fiber"],
                5
            ),
            self._score_based_on_thresholds(
                product.details["proteins_100g"].iloc[0],
                self._thresholds["protein"],
                5
            )
        ])
        
        return NutritionalScore(negative_points - positive_points)

    def rate(self, product: OpenFoodFactsProduct) -> str:
        """
        Convert numerical score to Nutri-Score grade (A-E).
        
        Args:
            product: OpenFoodFactsProduct instance
            
        Returns:
            str: Nutri-Score grade (A-E)
        """
        score = self.calculate_score(product)
        category = product.category.value
        
        ranges = {
            "solid": {
                (-float('inf'), -1): "A",
                (-1, 2): "B",
                (2, 10): "C",
                (10, 18): "D",
                (18, float('inf')): "E"
            },
            "beverage": {
                (-float('inf'), 0): "A",
                (0, 1): "B",
                (1, 5): "C",
                (5, 9): "D",
                (9, float('inf')): "E"
            }
        }
        
        for (min_score, max_score), grade in ranges[category].items():
            if min_score < score <= max_score:
                return grade
                
        return "E"  # Default grade if no range matches
    
class NutriscoreEvaluator(OpenFoodFactsProductEvaluator):
    
    def evaluate(self, product: OpenFoodFactsProduct, recommendation_strategy: RecommendationStrategy) -> float:
        if product.details.empty:
            raise ValueError("Cannot evaluate empty product")
            
        if "nutriscore_score" not in product.details.columns:
            raise ValueError("Product doesn't have nutriscore_score")
            
        score = float(product.details["nutriscore_score"].iloc[0])

        for factor in recommendation_strategy.recommendation_factors:
            if factor.name in product.details.columns:
                product_value = product.details[factor.name].iloc[0]
                if isinstance(product_value, str):
                    
                    if any(content in product_value for content in factor.content):
                        score = self._adjust_score(score, factor.weight, 
                                                recommendation_strategy.nutritional_rating_system.maximize_score)
                elif isinstance(factor.content, (int, float)) and factor.threshold:
                    if product_value >= factor.threshold:
                        score = self._adjust_score(score, factor.weight, 
                                                recommendation_strategy.nutritional_rating_system.maximize_score)

        return score
    
    def _adjust_score(self, current_score: float, weight: float, maximize: bool) -> float:
        return current_score + weight if maximize else current_score - weight
        
    