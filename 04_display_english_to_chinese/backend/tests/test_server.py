from fastapi.testclient import TestClient

from backend.server import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["translator_backend"] == "mock"


def test_test_caption_utf8_round_trip():
    client = TestClient(app)
    response = client.post(
        "/test-caption",
        json={
            "source_text": "Where is the train station?",
            "target_text": "火车站在哪里？",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["payload"]["target_text"] == "火车站在哪里？"
    assert body["payload"]["source_text"] == "Where is the train station?"
