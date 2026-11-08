"""API service tests (offline: pipeline is replaced by a fake)."""

import pytest

pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from src.api import main as api_main  # noqa: E402


class FakeResult:
    def to_dict(self):
        return {"topic": "测试话题", "citations": []}


class FakePipeline:
    def generate_lesson(self, **kwargs):
        return FakeResult()

    def generate_problem_solution(self, **kwargs):
        return FakeResult()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api_main, "_pipeline", lambda course: (FakePipeline(), None))
    return TestClient(api_main.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_reports_provider(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"llm_available", "provider", "model"}


def test_generate_lesson(client):
    response = client.post(
        "/api/generate/lesson",
        json={"topic": "机器学习基础", "duration": "2 小时", "cover_all": True},
    )
    assert response.status_code == 200
    assert response.json()["topic"] == "测试话题"


def test_generate_problem_solving_requires_problem_text(client):
    response = client.post("/api/generate/problem-solving", json={})
    assert response.status_code == 422


def test_generate_problem_solving_ok(client):
    response = client.post(
        "/api/generate/problem-solving",
        json={"problem_text": "如何缓解过拟合？"},
    )
    assert response.status_code == 200
    assert "topic" in response.json()
