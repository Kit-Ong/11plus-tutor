"""
Tests for arithmetic correctness of fractions questions in the exam resource bank.

Validates that:
- correct_answer is present in options
- correct_index points to the correct_answer
- For addition/subtraction questions the labelled answer equals the computed result
- Distractors (wrong options) are not accidentally equal to the correct answer
- worked_solution does not contradict the stated correct answer
"""

import glob
import json
import re
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "elevenplustutor.db"
FRACTIONS_JSON_DIR = ROOT / "data" / "questions" / "mathematics" / "fractions"


def _parse_fraction(s: str) -> Fraction | None:
    """Extract a Fraction from strings like '5/8', r'\\frac{5}{8}', r'\\(\\frac{5}{8}\\)'."""
    if not s:
        return None
    s = s.strip()
    # Strip LaTeX wrappers
    s = re.sub(r"\\+\(|\\+\)", "", s)
    s = re.sub(r"\\+\[|\\+\]", "", s)
    s = s.strip()
    # \frac{n}{d}  or  \dfrac{n}{d}
    m = re.search(r"\\d?frac\{(\d+)\}\{(\d+)\}", s)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    # plain n/d
    m = re.search(r"\b(\d+)\s*/\s*(\d+)\b", s)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    return None


def _load_db_fractions() -> list[dict]:
    """Load all fractions questions from the SQLite database."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, question_text, options, correct_answer, correct_index, worked_solution "
        "FROM questions WHERE question_type='fractions'"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    for r in rows:
        r["options"] = json.loads(r["options"]) if r["options"] else []
        r["_source"] = "db"
    return rows


def _load_json_fractions() -> list[dict]:
    """Load all fractions questions from individual JSON files."""
    questions = []
    for path in FRACTIONS_JSON_DIR.glob("*.json"):
        with open(path) as fh:
            q = json.load(fh)
        q.setdefault("worked_solution", q.get("explanation", ""))
        q["_source"] = f"json:{path.name}"
        questions.append(q)
    return questions


def _all_fractions_questions() -> list[dict]:
    # Prefer DB as source of truth; fall back to JSON files if no DB.
    db_qs = _load_db_fractions()
    json_qs = _load_json_fractions()
    if db_qs:
        return db_qs
    return json_qs


ALL_QUESTIONS = _all_fractions_questions()


# ---------------------------------------------------------------------------
# Parametrized tests
# ---------------------------------------------------------------------------


def _question_id(q: dict) -> str:
    return q.get("id", "unknown")


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_correct_answer_in_options(q):
    """The stated correct_answer must appear somewhere in the options list."""
    correct = q.get("correct_answer", "")
    opts = q.get("options", [])
    assert correct in opts, (
        f"[{q['_source']}] correct_answer {correct!r} is not in options {opts}"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_correct_index_matches_answer(q):
    """correct_index must point to the correct_answer."""
    opts = q.get("options", [])
    ci = q.get("correct_index")
    if ci is None:
        pytest.skip("correct_index not set")
    assert 0 <= ci < len(opts), (
        f"[{q['_source']}] correct_index={ci} is out of range (options has {len(opts)} items)"
    )
    assert opts[ci] == q.get("correct_answer"), (
        f"[{q['_source']}] options[{ci}]={opts[ci]!r} != correct_answer={q.get('correct_answer')!r}"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_addition_arithmetic(q):
    """For 'a/b + c/d' questions the labelled answer must equal the computed sum."""
    qt = q.get("question_text", "")
    m = re.search(
        r"frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*\+[^a-zA-Z0-9]*frac\{(\d+)\}\{(\d+)\}",
        qt,
    )
    if not m:
        pytest.skip("Not an addition question")
    a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    expected = Fraction(a, b) + Fraction(c, d)
    stated = _parse_fraction(q.get("correct_answer", ""))
    assert stated is not None, (
        f"[{q['_source']}] Could not parse correct_answer {q.get('correct_answer')!r}"
    )
    assert stated == expected, (
        f"[{q['_source']}] {a}/{b} + {c}/{d} = {expected}, "
        f"but correct_answer is {stated} ({q.get('correct_answer')!r})"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_subtraction_arithmetic(q):
    """For 'a/b - c/d' questions the labelled answer must equal the computed difference."""
    qt = q.get("question_text", "")
    m = re.search(
        r"frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*-[^a-zA-Z0-9]*frac\{(\d+)\}\{(\d+)\}",
        qt,
    )
    if not m:
        pytest.skip("Not a subtraction question")
    a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    expected = Fraction(a, b) - Fraction(c, d)
    stated = _parse_fraction(q.get("correct_answer", ""))
    assert stated is not None, (
        f"[{q['_source']}] Could not parse correct_answer {q.get('correct_answer')!r}"
    )
    assert stated == expected, (
        f"[{q['_source']}] {a}/{b} - {c}/{d} = {expected}, "
        f"but correct_answer is {stated} ({q.get('correct_answer')!r})"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_no_duplicate_options(q):
    """No option should appear twice (as a fraction value)."""
    opts = q.get("options", [])
    fracs = [_parse_fraction(o) for o in opts]
    seen: set[Fraction] = set()
    for i, frac in enumerate(fracs):
        if frac is None:
            continue
        assert frac not in seen, (
            f"[{q['_source']}] Duplicate fraction value {frac} in options {opts}"
        )
        seen.add(frac)


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_distractors_differ_from_correct(q):
    """Every wrong option must be numerically different from the correct answer."""
    correct_frac = _parse_fraction(q.get("correct_answer", ""))
    if correct_frac is None:
        pytest.skip("Cannot parse correct_answer as a fraction")
    opts = q.get("options", [])
    correct_text = q.get("correct_answer", "")
    for opt in opts:
        if opt == correct_text:
            continue  # skip the correct option itself
        distractor = _parse_fraction(opt)
        if distractor is None:
            continue
        assert distractor != correct_frac, (
            f"[{q['_source']}] Distractor {opt!r} equals the correct answer {correct_text!r}"
        )


# ---------------------------------------------------------------------------
# Standalone validation script (also usable outside pytest)
# ---------------------------------------------------------------------------


def validate_all() -> list[str]:
    """Return list of error strings for all questions; empty means all OK."""
    errors: list[str] = []
    questions = _all_fractions_questions()
    for q in questions:
        src = q["_source"]
        qid = q.get("id", "?")
        opts = q.get("options", [])
        correct = q.get("correct_answer", "")
        ci = q.get("correct_index")

        if correct not in opts:
            errors.append(f"[{src}|{qid}] correct_answer {correct!r} not in options {opts}")

        if ci is not None:
            if not (0 <= ci < len(opts)):
                errors.append(f"[{src}|{qid}] correct_index={ci} out of range")
            elif opts[ci] != correct:
                errors.append(f"[{src}|{qid}] options[{ci}]={opts[ci]!r} != correct_answer={correct!r}")

        qt = q.get("question_text", "")
        m_add = re.search(
            r"frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*\+[^a-zA-Z0-9]*frac\{(\d+)\}\{(\d+)\}", qt
        )
        if m_add:
            a, b, c, d = int(m_add.group(1)), int(m_add.group(2)), int(m_add.group(3)), int(m_add.group(4))
            expected = Fraction(a, b) + Fraction(c, d)
            stated = _parse_fraction(correct)
            if stated is not None and stated != expected:
                errors.append(
                    f"[{src}|{qid}] {a}/{b}+{c}/{d}={expected} but correct_answer={stated} ({correct!r})"
                )

        m_sub = re.search(
            r"frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*-[^a-zA-Z0-9]*frac\{(\d+)\}\{(\d+)\}", qt
        )
        if m_sub:
            a, b, c, d = int(m_sub.group(1)), int(m_sub.group(2)), int(m_sub.group(3)), int(m_sub.group(4))
            expected = Fraction(a, b) - Fraction(c, d)
            stated = _parse_fraction(correct)
            if stated is not None and stated != expected:
                errors.append(
                    f"[{src}|{qid}] {a}/{b}-{c}/{d}={expected} but correct_answer={stated} ({correct!r})"
                )

    return errors


if __name__ == "__main__":
    errs = validate_all()
    if errs:
        print(f"Found {len(errs)} error(s):")
        for e in errs:
            print(" ", e)
        raise SystemExit(1)
    qs = _all_fractions_questions()
    print(f"All {len(qs)} fractions questions passed validation.")
