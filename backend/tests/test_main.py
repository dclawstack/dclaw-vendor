from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_evaluation():
    response = client.post("/evaluations", json={"vendor_name": "TechCorp", "category": "IT"})
    assert response.status_code == 200
    data = response.json()
    assert data["vendor_name"] == "TechCorp"
    assert data["category"] == "IT"
    assert "id" in data

def test_get_alternatives():
    response = client.get("/evaluations/abc/alternatives")
    assert response.status_code == 200
    assert len(response.json()) == 2
