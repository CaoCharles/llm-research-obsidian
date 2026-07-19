import os
from unittest.mock import Mock, patch

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")

from fastapi.testclient import TestClient

import chat_server
from retrieval import RetrievedSource


client = TestClient(chat_server.app)


def test_health_reports_configured_backend():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["backend"] == "vertex-ai"
    assert response.json()["model"] == "gemini-3.5-flash"
    assert "retrieval" in response.json()


def test_chat_returns_frontend_contract():
    fake_response = Mock(text="Gemini API 測試成功")
    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    source = RetrievedSource(
        title="RAGAS 完整教學",
        url="https://example.test/ragas/",
        content="RAGAS 可用於評估 RAG 系統。",
        score=12.0,
    )
    with (
        patch.object(chat_server, "get_client", return_value=fake_client),
        patch.object(chat_server.retriever, "retrieve", return_value=[source]),
    ):
        response = client.post(
            "/api/chat",
            json={
                "history": [],
                "message": "hi",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "text": "Gemini API 測試成功",
        "sources": [{
            "title": "RAGAS 完整教學",
            "url": "https://example.test/ragas/",
        }],
    }
    call = fake_client.models.generate_content.call_args
    assert call.kwargs["model"] == "gemini-3.5-flash"
    instruction = call.kwargs["config"].system_instruction
    assert "RAGAS 完整教學" in instruction
    assert "https://example.test/ragas/" in instruction


def test_chat_rejects_invalid_role():
    response = client.post(
        "/api/chat",
        json={
            "history": [{"role": "bot", "parts": [{"text": "hello"}]}],
            "message": "hi",
        },
    )

    assert response.status_code == 422


def test_chat_still_works_when_retrieval_fails():
    fake_response = Mock(text="一般說明")
    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    with (
        patch.object(chat_server, "get_client", return_value=fake_client),
        patch.object(
            chat_server.retriever,
            "retrieve",
            side_effect=RuntimeError("content unavailable"),
        ),
    ):
        response = client.post("/api/chat", json={"message": "什麼是 LLM？"})

    assert response.status_code == 200
    assert response.json() == {"text": "一般說明", "sources": []}
