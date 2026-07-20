from fastapi.testclient import TestClient

from backend.app import app
from backend.session_store import SessionStore


def test_create_and_get_session() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/sessions",
        json={"question_set_id": "alpha", "created_by": "player-1"},
    )

    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    get_response = client.get(f"/api/sessions/{session_id}")

    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["session_id"] == session_id
    assert payload["question_set_id"] == "alpha"
    assert payload["created_by"] == "player-1"


def test_session_store_restores_join_and_answers_after_restart(tmp_path) -> None:
    store_path = tmp_path / "sessions.json"
    store = SessionStore(storage_path=store_path)
    session = store.create_session(question_set_id="alpha", created_by="player-1")

    store.join_session(session_id=session.session_id, joined_by="player-2")
    store.save_answer(
        session_id=session.session_id,
        player_id="player-2",
        perspective="impersonation",
        question_id=1,
        answer="A",
    )
    store.complete_session(session.session_id)

    restored_session = SessionStore(storage_path=store_path).get_session(session.session_id)

    assert restored_session is not None
    assert restored_session.joined_by == "player-2"
    assert restored_session.status == "completed"
    assert restored_session.data == {
        "answers": {"player-2": {"impersonation": {"1": "A"}}}
    }


def test_join_answer_resume_and_completion_flow() -> None:
    client = TestClient(app)
    session_id = client.post(
        "/api/sessions",
        json={"question_set_id": "alpha", "created_by": "player-1"},
    ).json()["session_id"]

    join_response = client.post(
        f"/api/sessions/{session_id}/join", json={"joined_by": "player-2"}
    )
    answer_response = client.post(
        f"/api/sessions/{session_id}/answers",
        json={
            "question_id": 1,
            "answer": "A",
            "player_id": "player-2",
            "perspective": "impersonation",
        },
    )
    resume_response = client.get(f"/api/sessions/{session_id}")
    complete_response = client.post(f"/api/sessions/{session_id}/complete")

    assert join_response.json()["status"] == "in_progress"
    assert answer_response.status_code == 200
    assert resume_response.json()["data"] == {
        "answers": {"player-2": {"impersonation": {"1": "A"}}}
    }
    assert complete_response.json()["status"] == "completed"
