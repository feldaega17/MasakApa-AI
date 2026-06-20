import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_empty_input():
    response = client.post("/recommend", json={"ingredients": ""})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()

def test_valid_ingredient_input():
    response = client.post("/recommend", json={"ingredients": "ayam, bawang putih, cabai"})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)

def test_response_structure():
    response = client.post("/recommend", json={"ingredients": "telur"})
    assert response.status_code == 200
    data = response.json()
    if data["recommendations"]:
        first_rec = data["recommendations"][0]
        assert "title" in first_rec
        assert "category" in first_rec
        assert "similarity_score" in first_rec
        assert "matched_ingredients" in first_rec
        assert "missing_ingredients" in first_rec
        assert "ingredients" in first_rec
        assert "steps" in first_rec
        assert "url" in first_rec
        assert "loves" in first_rec

def test_top_5_recommendations():
    response = client.post("/recommend", json={"ingredients": "ayam, bawang putih, cabai"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) <= 5

def test_similarity_score_range():
    response = client.post("/recommend", json={"ingredients": "ayam"})
    assert response.status_code == 200
    data = response.json()
    for rec in data["recommendations"]:
        assert 0.0 <= rec["similarity_score"] <= 1.0
