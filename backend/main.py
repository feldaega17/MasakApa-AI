from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.schemas import RecommendationRequest, RecommendationResponse
from backend.recommender import recommender_engine

app = FastAPI(
    title="MasakApa AI",
    description="API for recommending Indonesian recipes based on ingredients.",
    version="1.0.0"
)

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_recipes(request: RecommendationRequest):
    """
    Endpoint to recommend recipes based on input ingredients.
    Expects a comma-separated list of ingredients.
    """
    if not request.ingredients.strip():
        raise HTTPException(status_code=400, detail="Ingredients cannot be empty")
        
    try:
        recommendations = recommender_engine.get_recommendations(
            user_ingredients=request.ingredients,
            category=request.category,
            sort_by=request.sort_by
        )
        return RecommendationResponse(recommendations=recommendations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend directory for static assets if needed
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))
