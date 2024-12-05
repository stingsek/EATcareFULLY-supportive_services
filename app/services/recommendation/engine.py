from typing import List, Optional
import pandas as pd
from models.domain.off_product import OpenFoodFactsProduct
from services.recommendation.strategy import RecommendationStrategy
from services.recommendation.factors.recommendation_factor import FactorPreferenceStatus
from services.recommendation.evaluator.off_evaluator import OpenFoodFactsProductEvaluator
from services.recommendation.factors.nutritional_rating_systems.nutriscore import NutriscoreEvaluator
from heapq import nlargest, nsmallest, heappush
from utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)

class RecommendationEngine:
    """
    A recommendation engine that suggests alternative food products based on nutritional values and categories.

    The engine uses a multi-step filtering and ranking process:
    2. Excludes products with unwanted characteristics (based on recommendation factors)
    3. Evaluates and ranks remaining products using a configurable scoring system

    Key Features:
        - Customizable evaluation strategy for product scoring

    Attributes:
        recommendation_strategy: Defines scoring rules and factors to consider/avoid
        evaluator: Implements the product scoring logic
    """
    def __init__(self, recommendation_strategy: Optional[RecommendationStrategy] = None, evaluator: OpenFoodFactsProductEvaluator = NutriscoreEvaluator(), categories_similarity_threshold: float = 0.9) -> None:
        """
        Initializes the RecommendationEngine with the specified strategy, comparator, evaluator,
        and category similarity threshold.

        Args:
            recommendation_strategy (RecommendationStrategy): The strategy for scoring and ranking recommendations.
            evaluator (OpenFoodFactsProductEvaluator): Evaluator for product scoring.
        """
        self.recommendation_strategy = recommendation_strategy or RecommendationStrategy.create_default()
        self.evaluator = evaluator
        

    def find_recommendations(self, from_df: pd.DataFrame, product: OpenFoodFactsProduct, n=1) -> List[str]:
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
        logger.info(f"start finding recommendations for {product.code}")
        
        logger.info(f"start getting most similar products")
        _df = self.__get_most_similar_products(_df, product)
        
        logger.info(f"got {len(_df)} most similar products")
        
        logger.info(f"start excluding redundant products from {len(_df)} products")

        _df = self.__avoid_factors(_df)
        
        logger.info(f"redundant products excluded")
        
        logger.info(f"{len(_df)} products left after excluding redundant products")
        
        logger.info(f"Start getting {n} best recommendations if possible")

        recommendations = self.__get_n_best_recommendations(_df, product, n)
        
        return recommendations

    def __get_most_similar_products(self, from_df: pd.DataFrame, product: OpenFoodFactsProduct) -> pd.DataFrame:
        similarities = pd.read_csv("../data/similarities.csv")
        similarities['product1'] = similarities['product1'].astype(str).str.zfill(8)
        similarities['product2'] = similarities['product2'].astype(str).str.zfill(8)
        product_code = str(product.code).zfill(8)
    
        similarities = similarities[similarities['product1'] == product_code]
        from_df['code'] = from_df['code'].astype(str).str.zfill(8)
        from_df = from_df[from_df['code'].isin(similarities['product2'])]
        
        logger.info(f"Found {from_df}")
        
        return from_df
        
        

    def __get_n_best_recommendations(self, from_df: pd.DataFrame, product: OpenFoodFactsProduct, n: int = 1, have_better_rating: bool = True) -> List[str]:
        try:
            logger.info(f"Starting to evaluate {len(from_df)} products")
            evaluation_heap = self.__evaluate_all(from_df)
            
            if self.recommendation_strategy.nutritional_rating_system.maximize_score:
                best_n = [(score * -1, code) for score, code in nlargest(n, evaluation_heap)]
            else:
                best_n = nsmallest(n, evaluation_heap)
            
            logger.info(f"Found {len(best_n)} products with best scores")
            
            if have_better_rating:
                logger.info(f"Filtering products with better rating than source product")
                for score, code in best_n:
                    logger.info(f"Product {code} has a score of {score}")
                    best_n = [(score, code) for score, code in best_n if self.__compare_ratings(product, OpenFoodFactsProduct(code, from_df[from_df['code'].astype(str) == code].squeeze()))]
            
            if len(best_n) < n:
                logger.warning(f"Could not find enough products to recommend. Found {len(best_n)} products.")

            for score, code in best_n:
                logger.info(f"Product {code} has a score of {score}") 
            
            return [code for _, code in best_n]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    
    def __evaluate(self, product: OpenFoodFactsProduct) -> float:
        return self.evaluator.evaluate(product, self.recommendation_strategy.recommendation_factors)

    def __evaluate_all(self, df: pd.DataFrame) -> List[tuple[float, str]]:
        evaluation = []
        sign = -1 if self.recommendation_strategy.nutritional_rating_system.maximize_score else 1
        
        for _, row in df.iterrows():
            try:
                product = OpenFoodFactsProduct(row['code'], row)
                score = self.__evaluate(product)
                heappush(evaluation, (sign * score, str(row['code'])))
            except Exception as e:
                logger.warning(f"Failed to evaluate product {row['code']}: {str(e)}")
                continue
        return evaluation
    
    
    def __compare_ratings(self, product1: OpenFoodFactsProduct, product2: OpenFoodFactsProduct) -> bool:
        return self.recommendation_strategy.nutritional_rating_system.has_better_rating(product1, product2)

    # @lru_cache(maxsize=1000)
    # def __compare_categories(self, product_categories, target_categories):
    #     return self.categories_comparator.compare(product_categories, target_categories)

    # def __filter_categories(self, df: pd.DataFrame, product_categories) -> pd.DataFrame:
    #     logger.info(f"start filtering categories from {len(df)} products")
    #     df['similarity'] = df['categories_en'].apply(
    #         lambda x: self.__compare_categories(x, product_categories)
    #     )
    #     logger.info(f"ended filtering categories")
    #     return df[df['similarity'] >= self.categories_similarity_threshold].reset_index(drop=True)
        

    def __avoid_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"start avoiding factors from {len(df)} products")
        for factor in self.recommendation_strategy.recommendation_factors:
            if factor.status == FactorPreferenceStatus.AVOID:
                mask = ~df.apply(lambda x: factor.exists(x), axis=1)
                df = df[mask].reset_index(drop=True)
        return df
    
    # def __exclude_redundant_products(self, df: pd.DataFrame, product_categories) -> pd.DataFrame:
    #     return (df
    #                 .pipe(self.__filter_categories, product_categories)
    #                 .pipe(self.__avoid_factors))