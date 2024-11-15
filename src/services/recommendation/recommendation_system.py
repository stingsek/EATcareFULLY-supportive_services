from typing import List
import pandas as pd
from models.domain.off_product import OpenFoodFactsProduct


class RecommendationSystem:
    """
    High-level interface for product recommendations.
    
    Usage example:
        system = RecommendationSystem(
            recommendation_engine=RecommendationEngine(DefaultRecommendationStrategy)
        )
        
        recommendations = system.recommend(
            from_df=products_df,
            for_product=target_product,
            n=5
        )

    Args:
        recommendation_engine (RecommendationEngine): The recommendation engine instance that will handle
            the recommendation logic.
    """
    def __init__(self, recommendation_engine) -> None:
        self.recommendation_engine = recommendation_engine

    def recommend(self, from_df: pd.DataFrame, for_product: OpenFoodFactsProduct, n=1) -> List[int]:
        """
        Find and return recommended product IDs based on a target product.

        Args:
            from_df (pd.DataFrame): DataFrame containing product data.
            for_product (OpenFoodFactsProduct): The target product for which recommendations are generated.
            n (int): The number of recommendations to return.

        Returns:
            List[int]: A list of recommended product IDs.

        Example:
            recommendations = system.recommend(
                from_df=products_df,
                for_product=target_product,
                n=5
            )
        """
        return self.recommendation_engine.find_recommendations(from_df, for_product, n)
            