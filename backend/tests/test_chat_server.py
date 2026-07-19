import os
from unittest.mock import Mock, patch

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")

from fastapi.testclient import TestClient

import chat_server


client = TestClient(chat_server.app)


def test_health_reports_configured_backend():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["backend"] == "vertex-ai"
    assert response.json()["model"] == "gemini-2.5-flash"


def test_chat_returns_frontend_contract():
    fake_response = Mock(text="Gemini API 測試成功")
    fake_client = Mock()
    fake_client.models.generate_content.return_value = fake_response

    with patch.object(chat_server, "get_client", return_value=fake_client):
        response = client.post(
            "/api/chat",
            json={
                "history": [],
                "message": "hi",
                "system_instruction": "使用繁體中文",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"text": "Gemini API 測試成功"}
    call = fake_client.models.generate_content.call_args
    assert call.kwargs["model"] == "gemini-2.5-flash"


def test_chat_rejects_invalid_role():
    response = client.post(
        "/api/chat",
        json={
            "history": [{"role": "bot", "parts": [{"text": "hello"}]}],
            "message": "hi",
        },
    )

    assert response.status_code == 422
