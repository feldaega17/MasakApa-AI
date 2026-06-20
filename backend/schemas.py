from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationRequest(BaseModel):
    ingredients: str = Field(..., json_schema_extra={"example": "ayam, bawang putih, cabai"}, description="Comma separated list of ingredients")
    category: Optional[str] = Field(None, description="Optional category filter (e.g. Ayam, Sapi, Sayuran)")
    sort_by: Optional[str] = Field("relevance", description="Sort by 'relevance' or 'practicality'")

class RecipeRecommendation(BaseModel):
    title: str
    category: str
    similarity_score: float
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    ingredients: str
    steps: str
    url: str
    loves: int

class RecommendationResponse(BaseModel):
    recommendations: List[RecipeRecommendation]
