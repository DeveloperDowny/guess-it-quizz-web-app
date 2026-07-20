from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from threading import RLock
from typing import Any
import uuid


@dataclass
class SessionRecord:
    """Persisted state for one browser quiz session."""

    session_id: str
    question_set_id: str
    created_by: str
    question_set_snapshot: dict[str, Any] | None = None
    joined_by: str | None = None
    status: str = "created"
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of the session."""

        return {
            "session_id": self.session_id,
            "question_set_id": self.question_set_id,
            "created_by": self.created_by,
            "question_set_snapshot": self.question_set_snapshot,
            "joined_by": self.joined_by,
            "status": self.status,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SessionRecord":
        """Restore a session record that was written by :meth:`to_dict`."""

        return cls(
            session_id=str(payload["session_id"]),
            question_set_id=str(payload["question_set_id"]),
            created_by=str(payload["created_by"]),
            question_set_snapshot=payload.get("question_set_snapshot"),
            joined_by=(
                str(payload["joined_by"]) if payload.get("joined_by") is not None else None
            ),
            status=str(payload.get("status", "created")),
            data=dict(payload.get("data", {})),
        )


class SessionStore:
    """File-backed session repository used by the API layer.

    The small JSON store keeps local development sessions available after a server
    restart. The repository boundary allows a hosted datastore to replace it later.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path
        self._lock = RLock()
        self._sessions = self._load_sessions()

    def create_session(
        self,
        *,
        question_set_id: str,
        created_by: str,
        question_set_snapshot: dict[str, Any] | None = None,
    ) -> SessionRecord:
        with self._lock:
            session = SessionRecord(
                session_id=str(uuid.uuid4()),
                question_set_id=question_set_id,
                created_by=created_by,
                question_set_snapshot=question_set_snapshot,
            )
            self._sessions[session.session_id] = session
            self._save_sessions()
            return session

    def get_session(self, session_id: str) -> SessionRecord | None:
        with self._lock:
            return self._sessions.get(session_id)

    def join_session(self, *, session_id: str, joined_by: str) -> SessionRecord:
        """Register the second player and transition a new session to active."""

        with self._lock:
            session = self._require_session(session_id)
            if session.joined_by is not None and session.joined_by != joined_by:
                raise ValueError("session has already been joined")
            if joined_by == session.created_by:
                raise ValueError("the session creator cannot join as the second player")

            session.joined_by = joined_by
            if session.status == "created":
                session.status = "in_progress"
            self._save_sessions()
            return session

    def save_answer(
        self,
        *,
        session_id: str,
        player_id: str,
        perspective: str,
        question_id: int,
        answer: str,
    ) -> SessionRecord:
        """Persist one player answer without coupling storage to the UI."""

        with self._lock:
            session = self._require_session(session_id)
            if player_id not in {session.created_by, session.joined_by}:
                raise ValueError("player is not a participant in this session")
            if perspective not in {"self", "impersonation"}:
                raise ValueError("perspective must be 'self' or 'impersonation'")
            if session.status not in {"created", "in_progress"}:
                raise ValueError("answers cannot be changed after session completion")

            answers = session.data.setdefault("answers", {})
            player_answers = answers.setdefault(player_id, {})
            perspective_answers = player_answers.setdefault(perspective, {})
            perspective_answers[str(question_id)] = answer
            session.status = "in_progress"
            self._save_sessions()
            return session

    def complete_session(self, session_id: str) -> SessionRecord:
        """Mark a session as ready for judging."""

        with self._lock:
            session = self._require_session(session_id)
            if session.status == "created":
                raise ValueError("a session cannot be completed before a player joins")
            if session.status not in {"in_progress", "completed"}:
                raise ValueError("session cannot be completed in its current state")
            session.status = "completed"
            self._save_sessions()
            return session

    def _require_session(self, session_id: str) -> SessionRecord:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(session_id)
        return session

    def _load_sessions(self) -> dict[str, SessionRecord]:
        if self._storage_path is None or not self._storage_path.exists():
            return {}

        with self._storage_path.open(encoding="utf-8") as store_file:
            payload = json.load(store_file)
        if not isinstance(payload, dict):
            raise ValueError("session store must contain an object")
        return {
            session_id: SessionRecord.from_dict(session_payload)
            for session_id, session_payload in payload.items()
            if isinstance(session_payload, dict)
        }

    def _save_sessions(self) -> None:
        if self._storage_path is None:
            return

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._storage_path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as store_file:
            json.dump(
                {session_id: session.to_dict() for session_id, session in self._sessions.items()},
                store_file,
                indent=2,
                sort_keys=True,
            )
        temporary_path.replace(self._storage_path)
