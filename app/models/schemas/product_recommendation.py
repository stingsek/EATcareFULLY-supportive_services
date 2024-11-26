from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PreferenceValue(int):
    """Custom type for preference values to ensure they are only -1, 0, or 1"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v not in [-1, 0, 1]:
            raise ValueError('Preference value must be -1 (dislike), 0 (neutral), or 1 (like)')
        return v

class UserPreferences(BaseModel):
    preferences: Dict[str, PreferenceValue] = Field(
        default_factory=dict,
        description="User preferences for recommendations (-1: dislike, 0: neutral, 1: like)",
        examples=[{"milk": -1, "nuts": 1, "chocolate": 0}]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "preferences": {"milk": -1, "nuts": 1, "chocolate": 0}
            }
        }
    )

class ProductRecommendationRequest(BaseModel):
    product_code: str = Field(
        ...,
        min_length=8,
        max_length=48,
        pattern="^[a-zA-Z0-9]+$",
        description="Product code for which to get recommendations (EAN/SKU)",
        examples=["3017620425035"]
    )
    limit: int = Field(
        default=1,
        ge=1,
        le=50,
        description="Number of recommended products to return (1-50)"
    )
    user_preferences: Optional[UserPreferences] = Field(
        default=None,
        description="User preferences affecting recommendations"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_code": "3017620425035",
                "limit": 3,
                "user_preferences": {
                    "preferences": {"milk": -1, "nuts": 1}
                }
            }
        }
    )

class RecommendedProduct(BaseModel):
    code: str = Field(..., description="Product code (EAN/SKU)")
    name: str = Field(..., description="Product name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "3017620425036",
                "name": "Example Product",
            }
        }
    )

class ProductRecommendationResponse(BaseModel):
    source_product_code: str = Field(
        ..., 
        description="Product code for which recommendations were generated"
    )
    recommendations: List[RecommendedProduct] = Field(
        ..., 
        description="List of recommended products"
    )
    generation_time: float = Field(
        ...,
        ge=0,
        description="Time taken to generate recommendations (in seconds)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,  # zmiana z now na utcnow
        description="UTC timestamp when recommendations were generated"
    )
    total_found: int = Field(
        ..., 
        ge=0,
        description="Total number of potential recommendations found in the database"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_product_code": "3017620425035",
                "recommendations": [
                    {
                        "code": "3017620425036",
                        "name": "Example Product",
                    }
                ],
                "generation_time": 0.125,
                "timestamp": "2024-03-26T12:00:00Z",
                "total_found": 42
            }
        }
    )