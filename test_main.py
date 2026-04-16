from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_items():
    response = client.get("/items/42?q=TEST")
    assert response.status_code == 200
    assert response.json() == {"item_id": "42", "q": "TEST"}

def test_who():
    response = client.get("/who")
    assert response.status_code == 200
    assert "hostname" in response.json()

def test_random_gif():
    response = client.get("/random-gif")
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"].startswith("https://")
