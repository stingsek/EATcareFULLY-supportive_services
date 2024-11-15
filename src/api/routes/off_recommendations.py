from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from src.services.recommendation.recommendation_system import RecommendationSystem

router = APIRouter(prefix="/recommendations", tags=["recommendations"])