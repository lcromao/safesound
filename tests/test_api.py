import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    """Test main page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert "SafeSound" in response.text

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SafeSound API"

def test_get_models():
    """Test models endpoint"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "default" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) > 0

def test_upload_audio_no_file():
    """Test upload endpoint without file"""
    response = client.post("/api/upload_audio")
    assert response.status_code == 422  # Validation error

def test_upload_audio_invalid_file():
    """Test upload endpoint with invalid file type"""
    files = {"file": ("test.txt", b"fake content", "text/plain")}
    response = client.post("/api/upload_audio", files=files)
    assert response.status_code == 400
