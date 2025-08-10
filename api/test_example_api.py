from fastapi.testclient import TestClient
from example_api import app, memory_db

client = TestClient(app)

def test_get_fruits():
    memory_db["fruits"] = []  # clear state before test
    response = client.get("/fruits")  # ✅ fixed path
    assert response.status_code == 200
    assert response.json() == {"fruits": []}

def test_add_fruit():
    memory_db["fruits"] = []  # reset memory
    post_response = client.post("/fruits", json={"name": "banana"})
    assert post_response.status_code == 200
    assert post_response.json() == {"fruits": [{"name": "banana"}]}

    # Optional: confirm via GET
    get_response = client.get("/fruits")
    assert get_response.status_code == 200
    assert get_response.json() == {"fruits": [{"name": "banana"}]}