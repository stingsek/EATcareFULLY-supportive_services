from typing import List, Dict, Optional
from functools import lru_cache
import pandas as pd
from models.domain.off_product import OpenFoodFactsProduct
from app.services.recommendation.strategy import RecommendationStrategy
from logging import getLogger
import app.services.recommendation.factors.recommendation_factor as FactorStatus
from services.recommendation.factors.categories.categories_comparator import CategoriesComparator
from services.recommendation.evaluator.off_evaluator import OpenFoodFactsProductEvaluator
from services.text_processing.sentence_transformer_comparator import SentenceTransformerComparator
from services.recommendation.factors.nutritional_rating_systems.nutriscore import NutriscoreEvaluator
from heapq import nlargest, nsmallest, heappush

logger = getLogger(__name__)

class RecommendationEngine:
    """
    A recommendation engine that suggests alternative food products based on nutritional values and categories.

    The engine uses a multi-step filtering and ranking process:
    1. Filters products by category similarity using embeddings-based comparison
    2. Excludes products with unwanted characteristics (based on recommendation factors)
    3. Evaluates and ranks remaining products using a configurable scoring system

    Key Features:
        - Category-based filtering with configurable similarity threshold
        - Customizable evaluation strategy for product scoring
        - Support for different category comparison methods
        - Product completeness validation
        - Caching for category comparisons to improve performance

    Attributes:
        recommendation_strategy: Defines scoring rules and factors to consider/avoid
        categories_comparator: Handles comparison of product categories
        evaluator: Implements the product scoring logic
        categories_similarity_threshold: Minimum similarity score (0-1) for category matching
        product_completness_threshold: Minimum required product data completeness (0-1)
    """
    def __init__(self, recommendation_strategy: Optional[RecommendationStrategy] = None, categories_comparator: CategoriesComparator = SentenceTransformerComparator(), evaluator: OpenFoodFactsProductEvaluator = NutriscoreEvaluator(), categories_similarity_threshold: float = 0.9, product_completness_threshold: float = 0.5) -> None:
        """
        Initializes the RecommendationEngine with the specified strategy, comparator, evaluator,
        and category similarity threshold.

        Args:
            recommendation_strategy (RecommendationStrategy): The strategy for scoring and ranking recommendations.
            categories_comparator (CategoriesComparator): Comparator for assessing category similarity.
            evaluator (OpenFoodFactsProductEvaluator): Evaluator for product scoring.
            categories_similarity_threshold (float): Minimum score threshold for category matching.
        """
        self.recommendation_strategy = recommendation_strategy or RecommendationStrategy.create_default()
        self.categories_comparator = categories_comparator
        self.evaluator = evaluator
        self.categories_similarity_threshold = categories_similarity_threshold
        self.product_completness_threshold = product_completness_threshold
        

    def find_recommendations(self, from_df: pd.DataFrame, product: OpenFoodFactsProduct, n=1) -> List[int]:
        """
        Finds the top `n` recommended products for a given product based on similarity and scoring.

        Args:
            from_df (pd.DataFrame): DataFrame containing product data for generating recommendations.
            product (OpenFoodFactsProduct): The target product for which recommendations are sought.
            n (int, optional): Number of recommendations to return. Defaults to 1.

        Returns:
            List[int]: List of product codes for the top `n` recommendations.
        """
        _df = from_df.copy()

        product_categories = product.details["categories_en"].iloc[0]

        _df = self.__exclude_redundant_products(_df, product_categories)

        recommendations = self.__get_n_best_recommendations(_df, product, n)
            
        return recommendations


    def __exclude_redundant_products(self, df: pd.DataFrame, product_categories) -> pd.DataFrame:
        return (df
                    .pipe(self.__filter_categories, product_categories)
                    .pipe(self.__avoid_factors))


    def __get_n_best_recommendations(self, from_df: pd.DataFrame, product: OpenFoodFactsProduct, n: int = 1) -> List[str]:
        try:
            evaluation_heap = self.__evaluate_all(from_df)
            
            if self.recommendation_strategy.nutritional_rating_system.maximize_score:
                best_n = [(score * -1, code) for score, code in nlargest(n, evaluation_heap)]
            else:
                best_n = nsmallest(n, evaluation_heap)
                
            return [code for _, code in best_n]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def compare_ratings(self, product1: OpenFoodFactsProduct, product2: OpenFoodFactsProduct) -> float:
        return self.recommendation_strategy.nutritional_rating_system.compare_ratings(product1, product2)
        

    def __evaluate(self, product: OpenFoodFactsProduct) -> float:
        return self.evaluator.evaluate(product, self.recommendation_strategy)

    def __evaluate_all(self, df: pd.DataFrame) -> List[tuple[float, str]]:
        evaluation = []
        sign = -1 if self.recommendation_strategy.nutritional_rating_system.maximize_score else 1
        
        for _, row in df.iterrows():
            try:
                product = OpenFoodFactsProduct(row['code'], row)
                score = self.__evaluate(product)
                heappush(evaluation, (sign * score, row['code']))
            except Exception as e:
                logger.warning(f"Failed to evaluate product {row['code']}: {str(e)}")
                continue
        return evaluation
    

    @lru_cache(maxsize=1000)
    def __compare_categories(self, product_categories, target_categories):
        return self.categories_comparator.compare(product_categories, target_categories)

    def __filter_categories(self, df: pd.DataFrame, product_categories) -> pd.DataFrame:
        df['similarity'] = df['categories_en'].apply(
            lambda x: self.__compare_categories(x, product_categories)
        )
        return df[df['similarity'] >= self.categories_similarity_threshold].reset_index(drop=True)
        

    def __avoid_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        for factor in self.recommendation_strategy.recommendation_factors:
            if factor.status == FactorStatus.AVOID:
                mask = ~df.apply(lambda x: factor.exists(x), axis=1)
                df = df[mask].reset_index(drop=True)
        return df
        