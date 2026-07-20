from fastapi.testclient import TestClient

from backend.app import app


def test_question_retrieval_and_answer_submission(tmp_path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    (questions_dir / "alpha.yaml").write_text(
        "questions:\n"
        "  - id: 1\n"
        "    question: 'Who?'\n"
        "    options:\n"
        "      - 'A'\n"
        "      - 'B'\n",
        encoding="utf-8",
    )

    client = TestClient(app)
    create_response = client.post(
        "/api/sessions",
        json={"question_set_id": "alpha", "created_by": "player-1"},
    )
    session_id = create_response.json()["session_id"]

    questions_response = client.get(
        f"/api/sessions/{session_id}/questions",
        params={"questions_dir": str(questions_dir)},
    )
    assert questions_response.status_code == 200
    assert questions_response.json()["question_set_id"] == "alpha"
    assert questions_response.json()["questions"][0]["id"] == 1

    answer_response = client.post(
        f"/api/sessions/{session_id}/answers",
        json={"question_id": 1, "answer": "A"},
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["status"] == "ok"


def test_session_keeps_question_snapshot_when_source_changes(tmp_path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    question_file = questions_dir / "alpha.yaml"
    question_file.write_text(
        "questions:\n  - id: 1\n    question: 'Original?'\n    options: ['A', 'B']\n",
        encoding="utf-8",
    )
    client = TestClient(app)
    session_id = client.post(
        "/api/sessions",
        json={
            "question_set_id": "alpha",
            "created_by": "player-1",
            "questions_dir": str(questions_dir),
        },
    ).json()["session_id"]
    question_file.write_text(
        "questions:\n  - id: 1\n    question: 'Changed?'\n    options: ['C', 'D']\n",
        encoding="utf-8",
    )

    response = client.get(f"/api/sessions/{session_id}/questions")

    assert response.status_code == 200
    assert response.json()["questions"][0]["question"] == "Original?"


def test_judge_endpoint_returns_match_breakdown(tmp_path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    (questions_dir / "alpha.yaml").write_text(
        "questions:\n"
        "  - id: 1\n"
        "    question: 'Colour?'\n"
        "    options: ['Blue', 'Green']\n"
        "  - id: 2\n"
        "    question: 'Number?'\n"
        "    options: ['One', 'Two']\n",
        encoding="utf-8",
    )
    client = TestClient(app)
    session_id = client.post(
        "/api/sessions",
        json={"question_set_id": "alpha", "created_by": "one", "questions_dir": str(questions_dir)},
    ).json()["session_id"]
    client.post(f"/api/sessions/{session_id}/join", json={"joined_by": "two"})
    for player, self_answers, impersonation in [
        ("one", ["Blue", "One"], ["Green", "Two"]),
        ("two", ["Green", "Two"], ["Blue", "Two"]),
    ]:
        for question_id, answer in enumerate(self_answers, 1):
            client.post(f"/api/sessions/{session_id}/answers", json={"question_id": question_id, "answer": answer, "player_id": player, "perspective": "self"})
        for question_id, answer in enumerate(impersonation, 1):
            client.post(f"/api/sessions/{session_id}/answers", json={"question_id": question_id, "answer": answer, "player_id": player, "perspective": "impersonation"})
    client.post(f"/api/sessions/{session_id}/complete")

    response = client.get(f"/api/sessions/{session_id}/judge")

    assert response.status_code == 200
    assert response.json()["results"][0]["matched_answers"] == 2
    assert response.json()["results"][0]["reviews"][0]["is_match"] is True
    assert response.json()["results"][1]["matched_answers"] == 1
