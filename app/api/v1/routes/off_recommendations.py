from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas.product_recommendation import (
    ProductRecommendationResponse, 
    ProductRecommendationRequest, 
    UserPreferences
)
import logging
from time import time
from fastapi import Depends
from app.dependencies import get_recommendation_service
from app.services.recommendation.service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["api", "v1"]
)

@router.get(
    "/recommendations/{product_id}",
    response_model=ProductRecommendationResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def get_recommendations_for_product(
    product_id: str,
    limit: int = Query(
        default=1, 
        ge=1, 
        le=50,
        description="Number of recommendations to return"
    ),
    user_preferences: Optional[UserPreferences] = None,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> ProductRecommendationResponse:
    """
    Get product recommendations based on product ID and optional user preferences.
    
    Args:
        product_id: Product identifier
        limit: Number of recommendations to return (1-50)
        user_preferences: Optional user preferences for personalization
        recommendation_service: Injected recommendation service
        
    Returns:
        ProductRecommendationResponse with recommendations
    """
    try:
        request = ProductRecommendationRequest(
            product_code=product_id,
            limit=limit,
            user_preferences=user_preferences
        )
        
        # Pomiar czasu
        start_time = time()
        
        # Generowanie rekomendacji
        recommendations = await recommendation_service.generate_recommendations(request)
        
        # Obliczanie czasu generowania
        generation_time = time() - start_time
        
        return ProductRecommendationResponse(
            source_product_code=product_id,
            recommendations=recommendations,
            generation_time=generation_time,
            total_found=len(recommendations)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "message": str(e)
            }
        )
    except Exception as e:
        # Można też dodać logowanie błędu
        logger.exception(f"Error generating recommendations for {product_id}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )
