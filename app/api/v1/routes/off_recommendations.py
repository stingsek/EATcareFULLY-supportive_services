from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import ProductRecommendation, RecommendationResponse
from app.services.recommendation.service import generate_recommendations

router = APIRouter(prefix="/api/v1/", tags=["api","v1"])





@router.get("/recommendations/{product_id}")
async def get_recommendations_with_params(
    product_id: str,
    limit: int = 5,
    min_score: float = 0.0,
    category: Optional[str] = None
):
    try:
        recommendations = await generate_recommendations(product_id)
        filtered_recommendations = [
            rec for rec in recommendations 
            if rec.score >= min_score
            and (category is None or rec.category == category)
        ][:limit]
        
        return RecommendationResponse(
            requested_product_id=product_id,
            recommendations=filtered_recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

