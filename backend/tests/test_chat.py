from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ingest_then_ask_returns_grounded_answer():
    ingest_response = client.post(
        "/api/docs/ingest",
        json={
            "document_name": "runbook-deploys.md",
            "text": (
                "To roll back a bad deploy, run `kubectl rollout undo "
                "deployment/compass-backend` in the target namespace. "
                "This reverts to the previous ReplicaSet within seconds."
            ),
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["chunks_indexed"] >= 1

    chat_response = client.post("/api/chat", json={"question": "How do I roll back a bad deploy?"})
    assert chat_response.status_code == 200
    body = chat_response.json()
    assert "answer" in body
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["document"] == "runbook-deploys.md"
