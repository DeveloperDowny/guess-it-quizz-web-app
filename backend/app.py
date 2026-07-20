from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from quizz.domain.models import AnswerSheet, QuestionSet
from quizz.services.judge_service import JudgeService

from backend.question_set_service import QuestionSetService
from backend.quiz_adapter import QuizAdapter
from backend.session_store import SessionStore

def cors_origins_from_environment() -> list[str]:
    """Read the explicit frontend-origin allowlist from the environment."""

    configured = os.getenv("QUIZZ_CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(title="Quizz Browser Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_from_environment(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.state.session_store = SessionStore(storage_path=Path("data/sessions.json"))
app.state.quiz_adapter = QuizAdapter()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health payload for deployment and smoke tests."""

    return {"status": "ok"}


@app.get("/api/question-sets")
def list_question_sets(
    questions_dir: Annotated[str | None, Query()] = None,
) -> dict[str, list[str]]:
    """List available question-set identifiers discovered from the questions directory."""

    target_dir = Path(questions_dir) if questions_dir else Path("questions")
    service = QuestionSetService(questions_dir=target_dir)
    return {"question_sets": service.list_question_sets()}


@app.post("/api/sessions")
def create_session(payload: dict[str, str]) -> dict[str, str]:
    """Create a new session bound to a selected question set."""

    question_set_id = payload.get("question_set_id", "")
    created_by = payload.get("created_by", "")
    if not question_set_id or not created_by:
        raise HTTPException(
            status_code=400, detail="question_set_id and created_by are required"
        )

    snapshot = None
    questions_dir = "questions"
    if questions_dir:
        service = QuestionSetService(
            questions_dir=Path(questions_dir), quiz_adapter=app.state.quiz_adapter
        )
        try:
            snapshot = service.load_question_set(question_set_id).model_dump()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="question set not found") from None
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    session = app.state.session_store.create_session(
        question_set_id=question_set_id,
        created_by=created_by,
        question_set_snapshot=snapshot,
    )
    return {"session_id": session.session_id}


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, object]:
    """Retrieve an existing session by ID."""

    session = app.state.session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_id": session.session_id,
        "question_set_id": session.question_set_id,
        "created_by": session.created_by,
        "joined_by": session.joined_by,
        "status": session.status,
        "data": session.data,
    }


@app.post("/api/sessions/{session_id}/join")
def join_session(session_id: str, payload: dict[str, str]) -> dict[str, object]:
    """Join a session as its second player."""

    joined_by = payload.get("joined_by", "")
    if not joined_by:
        raise HTTPException(status_code=400, detail="joined_by is required")
    try:
        session = app.state.session_store.join_session(
            session_id=session_id, joined_by=joined_by
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found") from None
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return {
        "session_id": session.session_id,
        "question_set_id": session.question_set_id,
        "joined_by": session.joined_by,
        "status": session.status,
    }


@app.get("/api/sessions/{session_id}/questions")
def get_session_questions(
    session_id: str, questions_dir: Annotated[str | None, Query()] = None
) -> dict[str, object]:
    """Return the question set bound to a session."""

    session = app.state.session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    if session.question_set_snapshot is not None:
        question_set = QuestionSet.model_validate(session.question_set_snapshot)
    else:
        target_dir = Path(questions_dir) if questions_dir else Path("questions")
        question_set_path = target_dir / f"{session.question_set_id}.yaml"
        question_set = app.state.quiz_adapter.load_question_set(question_set_path)

    return {
        "session_id": session.session_id,
        "question_set_id": session.question_set_id,
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "options": question.options,
            }
            for question in question_set.questions
        ],
    }


@app.post("/api/sessions/{session_id}/answers")
def submit_answer(session_id: str, payload: dict[str, str | int]) -> dict[str, str]:
    """Store an answer for a session."""

    session = app.state.session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    question_id = payload.get("question_id")
    answer = payload.get("answer")
    if not isinstance(question_id, int) or not isinstance(answer, str) or not answer:
        raise HTTPException(
            status_code=400, detail="question_id and answer are required"
        )

    player_id = payload.get("player_id", session.created_by)
    perspective = payload.get("perspective", "self")
    if not isinstance(player_id, str) or not player_id:
        raise HTTPException(status_code=400, detail="player_id is required")
    if not isinstance(perspective, str):
        raise HTTPException(status_code=400, detail="perspective is required")

    try:
        app.state.session_store.save_answer(
            session_id=session_id,
            player_id=player_id,
            perspective=perspective,
            question_id=question_id,
            answer=answer,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"status": "ok"}


@app.post("/api/sessions/{session_id}/complete")
def complete_session(session_id: str) -> dict[str, str]:
    """Mark a joined session as completed and ready for judging."""

    try:
        session = app.state.session_store.complete_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found") from None
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"session_id": session.session_id, "status": session.status}


@app.get("/api/sessions/{session_id}/judge")
def get_judge_result(session_id: str) -> dict[str, object]:
    """Score both players' impersonation answers against the other player's self answers."""

    session = app.state.session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    if session.status not in {"completed", "judged"}:
        raise HTTPException(status_code=409, detail="session must be completed before judging")
    if not session.joined_by:
        raise HTTPException(status_code=400, detail="both players must join before judging")

    try:
        if session.question_set_snapshot is None:
            raise ValueError("session has no validated question-set snapshot")
        question_set = QuestionSet.model_validate(session.question_set_snapshot)
        raw_answers = session.data.get("answers", {})
        players = [session.created_by, session.joined_by]
        sheets = {
            player: {
                perspective: AnswerSheet.model_validate({"answers": [
                    {"question-id": int(question_id), "answer": answer}
                    for question_id, answer in raw_answers.get(player, {}).get(perspective, {}).items()
                ]})
                for perspective in ("self", "impersonation")
            }
            for player in players
        }
        for player in players:
            if not raw_answers.get(player, {}).get("self") or not raw_answers.get(player, {}).get("impersonation"):
                raise ValueError(f"missing self or impersonation answers for {player}")
    except (TypeError, ValueError, KeyError) as error:
        raise HTTPException(status_code=400, detail=f"session answers are incomplete: {error}") from error

    judgements = []
    judge_service = JudgeService()
    for player, target in ((players[0], players[1]), (players[1], players[0])):
        result = judge_service.evaluate(
            question_set=question_set,
            player_name=player,
            target_name=target,
            player_impersonation_sheet=sheets[player]["impersonation"],
            target_actual_sheet=sheets[target]["self"],
        )
        judgements.append({
            "player_name": result.player_name,
            "target_name": result.target_name,
            "matched_answers": result.matched_answers,
            "total_questions": result.total_questions,
            "reviews": [
                {
                    "question_id": review.question.id,
                    "question": review.question.question,
                    "guessed_answer": review.guessed_answer,
                    "correct_answer": review.correct_answer,
                    "is_match": review.is_match,
                }
                for review in result.reviews
            ],
        })

    return {"session_id": session.session_id, "results": judgements}
