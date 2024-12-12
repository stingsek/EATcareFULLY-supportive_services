from fastapi import APIRouter, HTTPException, Body
from models.schemas.product_recommendation import (
    ProductRecommendationResponse, 
    ProductRecommendationRequest, 
)
from time import time
from fastapi import Depends
from dependencies import get_recommendation_service
from services.recommendation.service import RecommendationService
from utils.logger import setup_colored_logger

logger = setup_colored_logger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["api", "v1"]
)

@router.post(
    "/recommendations/",
    response_model=ProductRecommendationResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def get_recommendations_for_product(
    request: ProductRecommendationRequest = Body(...),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> ProductRecommendationResponse:
    """
    Get product recommendations based on request data.
    
    Args:
        request: ProductRecommendationRequest containing product_code, limit, and preferences
        recommendation_service: Injected recommendation service
        
    Returns:
        ProductRecommendationResponse with recommendations
    """
    try:
        start_time = time()
        recommendations = await recommendation_service.generate_recommendations(request)
        generation_time = time() - start_time
        
        logger.info(f"product_id: {request.product_code}")
        logger.info(f"Generated {len(recommendations)} recommendations in {generation_time:.2f} seconds")
        
        return ProductRecommendationResponse(
            source_product_code=request.product_code,
            recommendations=recommendations,
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
        logger.exception(f"Error generating recommendations for {request.product_code}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )
