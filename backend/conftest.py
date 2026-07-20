import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZZ_SRC = ROOT / "quizz-cli-app" / "quizz" / "src"

if str(QUIZZ_SRC) not in sys.path:
    sys.path.insert(0, str(QUIZZ_SRC))
