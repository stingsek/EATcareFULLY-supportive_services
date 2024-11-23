from typing import List, Optional, Annotated
from pydantic import BaseModel


class ProductRecommendationRequest(BaseModel):
    product_code: str
    limit: Optional[int] = 5
    categories_weight: Optional[float] = 1.0
    nutriscore_weight: Optional[float] = 1.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_code": "3017620425035",
                "limit": 5
            }
        }


class RecommendedProduct(BaseModel):
    code: str
    name: str
    
    
class ProductRecommendationResponse(BaseModel):
    source_product: str
    recommendations: List[RecommendedProduct]
    recommendation_time: str