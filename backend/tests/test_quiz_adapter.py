from pathlib import Path

import pytest

from backend.quiz_adapter import QuizAdapter


def test_load_question_set_uses_existing_yaml_schema(tmp_path: Path) -> None:
    questions_path = tmp_path / "demo.yaml"
    questions_path.write_text(
        "questions:\n"
        "  - id: 1\n"
        "    question: 'What is 2 + 2?'\n"
        "    options:\n"
        "      - '3'\n"
        "      - '4'\n"
        "      - '5'\n",
        encoding="utf-8",
    )

    adapter = QuizAdapter()

    question_set = adapter.load_question_set(questions_path)

    assert [question.id for question in question_set.questions] == [1]
    assert question_set.questions[0].options == ["3", "4", "5"]


def test_build_answer_sheet_rejects_invalid_option(tmp_path: Path) -> None:
    questions_path = tmp_path / "demo.yaml"
    questions_path.write_text(
        "questions:\n"
        "  - id: 1\n"
        "    question: 'What is 2 + 2?'\n"
        "    options:\n"
        "      - '3'\n"
        "      - '4'\n"
        "      - '5'\n",
        encoding="utf-8",
    )

    adapter = QuizAdapter()
    question_set = adapter.load_question_set(questions_path)

    with pytest.raises(ValueError, match="Invalid answer"):
        adapter.build_answer_sheet(question_set=question_set, answer_map={1: "wrong"})
