from fastapi.testclient import TestClient

from backend.app import app, cors_origins_from_environment


def test_health_check() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_question_sets_endpoint_lists_available_sets(tmp_path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    (questions_dir / "alpha.yaml").write_text("questions: []\n", encoding="utf-8")
    (questions_dir / "beta.yaml").write_text("questions: []\n", encoding="utf-8")

    client = TestClient(app)
    response = client.get(
        "/api/question-sets", params={"questions_dir": str(questions_dir)}
    )

    assert response.status_code == 200
    assert response.json() == {"question_sets": ["alpha", "beta"]}


def test_cors_preflight_allows_configured_frontend_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in response.headers


def test_cors_rejects_unconfigured_frontend_origin() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={"Origin": "https://untrusted.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_origins_are_read_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "QUIZZ_CORS_ORIGINS", "https://quiz.example, https://staging.quiz.example"
    )

    assert cors_origins_from_environment() == [
        "https://quiz.example",
        "https://staging.quiz.example",
    ]
