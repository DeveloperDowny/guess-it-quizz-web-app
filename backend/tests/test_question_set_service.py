from pathlib import Path

from backend.question_set_service import QuestionSetService


def test_list_question_sets_returns_file_ids(tmp_path: Path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    (questions_dir / "alpha.yaml").write_text("questions: []\n", encoding="utf-8")
    (questions_dir / "beta.yaml").write_text("questions: []\n", encoding="utf-8")

    service = QuestionSetService(questions_dir=questions_dir)

    assert service.list_question_sets() == ["alpha", "beta"]


def test_load_question_set_validates_yaml(tmp_path: Path) -> None:
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    (questions_dir / "alpha.yaml").write_text(
        "questions:\n"
        "  - id: 1\n"
        "    question: 'Who?'\n"
        "    options: ['A', 'B']\n",
        encoding="utf-8",
    )

    question_set = QuestionSetService(questions_dir=questions_dir).load_question_set("alpha")

    assert question_set.questions[0].options == ["A", "B"]
