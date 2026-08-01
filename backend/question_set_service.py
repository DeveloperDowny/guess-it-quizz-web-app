from __future__ import annotations

from pathlib import Path

from impersonation_quizz.domain.models import QuestionSet

from backend.quiz_adapter import QuizAdapter


class QuestionSetService:
    """Discover and expose question-set definitions from the questions directory."""

    def __init__(
        self, *, questions_dir: Path, quiz_adapter: QuizAdapter | None = None
    ) -> None:
        self._questions_dir = questions_dir
        self._quiz_adapter = quiz_adapter or QuizAdapter()

    def list_question_sets(self) -> list[str]:
        """Return sorted question-set identifiers from YAML files in the questions directory."""

        if not self._questions_dir.exists():
            return []

        return sorted(
            path.stem for path in self._questions_dir.glob("*.yaml") if path.is_file()
        )

    def load_question_set(self, question_set_id: str) -> QuestionSet:
        """Load and validate a discovered question set by its stable identifier."""

        if question_set_id not in self.list_question_sets():
            raise FileNotFoundError(f"Question set not found: {question_set_id}")
        return self._quiz_adapter.load_question_set(
            self._questions_dir / f"{question_set_id}.yaml"
        )
