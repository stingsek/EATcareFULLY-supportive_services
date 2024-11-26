from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas.product import ProductRecommendationResponse, ProductRecommendationRequest, UserPreferences
from app.services.recommendation.service import generate_recommendations
from time import time

router = APIRouter(prefix="/api/v1/", tags=["api","v1"])


@router.get("/recommendations/{product_id}", response_model=ProductRecommendationResponse)
async def get_recommendations_for_product(
    product_id: str,
    limit: int = Query(default=1, ge=1, le=50),
    user_preferences: Optional[UserPreferences] = None
):
    try:
        request = ProductRecommendationRequest(
            product_code=product_id,
            limit=limit,
            user_preferences=user_preferences
        )
        start_time = time.time()
        
        recommendations = await generate_recommendations(request)
        
        generation_time = time.time() - start_time
        
        return ProductRecommendationResponse(
        source_product_code=product_id,
        recommendations=recommendations,
        generation_time=generation_time,
        total_found=len(recommendations)
    )
    except ValueError as e:
        # validation
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # internal server error
        raise HTTPException(status_code=500, detail=str(e))
