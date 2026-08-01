from __future__ import annotations

from pathlib import Path

from impersonation_quizz.domain.models import AnswerEntry, AnswerSheet, QuestionSet
from impersonation_quizz.infrastructure.yaml_repository import YamlQuizRepository


class QuizAdapter:
    """Expose the existing quiz domain logic to the web backend."""

    def __init__(self, repository: YamlQuizRepository | None = None) -> None:
        self._repository = repository or YamlQuizRepository()

    def load_question_set(self, file_path: Path) -> QuestionSet:
        """Load and validate a question set using the existing YAML repository."""

        return self._repository.load_questions(file_path)

    def build_answer_sheet(
        self, *, question_set: QuestionSet, answer_map: dict[int, str]
    ) -> AnswerSheet:
        """Build a validated answer sheet from a question-id to answer mapping."""

        answers: list[AnswerEntry] = []
        for question in question_set.questions:
            selected_answer = answer_map.get(question.id, "")
            if selected_answer not in question.options:
                raise ValueError(
                    f"Invalid answer '{selected_answer}' for question {question.id}. "
                    f"Expected one of: {question.options}"
                )
            answers.append(AnswerEntry(question_id=question.id, answer=selected_answer))

        return AnswerSheet(answers=answers)
