"""
Tests for arithmetic correctness of fractions questions in the exam resource bank.

Validates that:
- correct_answer is present in options
- correct_index points to the correct_answer
- For addition/subtraction questions (LaTeX or verbal) the labelled answer equals the computed result
- Simplification questions give the reduced form of the stated fraction
- Denominator-conversion questions give the correct scaled fraction
- Distractors (wrong options) are not accidentally equal to the correct answer

Test types and what they cover
-------------------------------
test_addition_arithmetic          LaTeX: \frac{a}{b} + \frac{c}{d}  (also \dfrac)
test_verbal_addition_arithmetic   English: "adding A and B" / "sum of A and B"
test_subtraction_arithmetic       LaTeX: \frac{a}{b} - \frac{c}{d}  (also \dfrac)
test_verbal_subtraction_arithmetic English: "subtracting A from B"  (result = B - A)
test_simplification_arithmetic    "equivalent to" / "simplest form of" a single fraction
test_denominator_conversion       "equivalent to X/Y with a denominator of D"
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
# Compiled regex patterns shared across tests
# ---------------------------------------------------------------------------

# LaTeX inline addition/subtraction (\frac or \dfrac)
_LATEX_ADD_PAT = re.compile(
    r"d?frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*\+[^a-zA-Z0-9]*d?frac\{(\d+)\}\{(\d+)\}"
)
_LATEX_SUB_PAT = re.compile(
    r"d?frac\{(\d+)\}\{(\d+)\}[^a-zA-Z0-9]*-[^a-zA-Z0-9]*d?frac\{(\d+)\}\{(\d+)\}"
)

# Verbal addition: "adding A and B" / "sum of A and B" / "result of adding A and B"
_VERBAL_ADD_PAT = re.compile(
    r"(?:result of adding|adding|sum of)\b.*?"
    r"(?:d?frac)\{(\d+)\}\{(\d+)\}.*?"
    r"\band\b.*?"
    r"(?:d?frac)\{(\d+)\}\{(\d+)\}",
    re.IGNORECASE | re.DOTALL,
)

# Verbal subtraction: "subtracting A from B"  → answer = B - A
_VERBAL_SUB_PAT = re.compile(
    r"subtracting\s+.*?(?:d?frac)\{(\d+)\}\{(\d+)\}.*?from\s+.*?(?:d?frac)\{(\d+)\}\{(\d+)\}",
    re.IGNORECASE | re.DOTALL,
)

# Detect any explicit operation between two bracketed fractions (rules out simplification)
_FRAC_OP_PAT = re.compile(
    r"d?frac\{[^}]+\}\{[^}]+\}[^a-zA-Z\d]*[+\-]"
)
# Detect operation keywords in prose
_OP_KEYWORD_PAT = re.compile(
    r"\b(?:adding|subtracting|sum of|plus|minus|result)\b", re.IGNORECASE
)

# Simplification: "equivalent to" or "simplest form of" a single fraction (no operation)
_SIMPLIFY_PAT = re.compile(
    r"(?:equivalent to|simplest form of)\s+[^?!.]*?(?:d?frac)\{(\d+)\}\{(\d+)\}",
    re.IGNORECASE,
)

# Denominator conversion: "equivalent to N/D when expressed with a denominator of T"
_DENOM_CONV_PAT = re.compile(
    r"equivalent to\s+(\d+)/(\d+).*?denominator\s+of\s+(\d+)",
    re.IGNORECASE | re.DOTALL,
)


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
    """LaTeX inline 'a/b + c/d' (\\frac or \\dfrac): answer must equal computed sum."""
    qt = q.get("question_text", "")
    m = _LATEX_ADD_PAT.search(qt)
    if not m:
        pytest.skip("No LaTeX inline addition pattern found")
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
def test_verbal_addition_arithmetic(q):
    """Verbal 'adding A and B' / 'sum of A and B': answer must equal computed sum."""
    qt = q.get("question_text", "")
    m = _VERBAL_ADD_PAT.search(qt)
    if not m:
        pytest.skip("No verbal addition pattern found")
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
    """LaTeX inline 'a/b - c/d' (\\frac or \\dfrac): answer must equal computed difference."""
    qt = q.get("question_text", "")
    m = _LATEX_SUB_PAT.search(qt)
    if not m:
        pytest.skip("No LaTeX inline subtraction pattern found")
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
def test_verbal_subtraction_arithmetic(q):
    """Verbal 'subtracting A from B': answer must equal B - A."""
    qt = q.get("question_text", "")
    m = _VERBAL_SUB_PAT.search(qt)
    if not m:
        pytest.skip("No verbal subtraction pattern found")
    # Groups: 1,2 = the subtracted fraction A; 3,4 = the fraction it is subtracted FROM (B)
    a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    expected = Fraction(c, d) - Fraction(a, b)  # B - A
    stated = _parse_fraction(q.get("correct_answer", ""))
    assert stated is not None, (
        f"[{q['_source']}] Could not parse correct_answer {q.get('correct_answer')!r}"
    )
    assert stated == expected, (
        f"[{q['_source']}] {c}/{d} - {a}/{b} = {expected}, "
        f"but correct_answer is {stated} ({q.get('correct_answer')!r})"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_simplification_arithmetic(q):
    """'Equivalent to' / 'simplest form of' a single fraction: answer must equal the reduced fraction."""
    qt = q.get("question_text", "")
    # Skip questions that contain operational keywords or an explicit +/- between fractions
    if _OP_KEYWORD_PAT.search(qt):
        pytest.skip("Question has operation keywords – not a pure simplification question")
    if _FRAC_OP_PAT.search(qt):
        pytest.skip("Question has a +/- operator between fractions")
    m = _SIMPLIFY_PAT.search(qt)
    if not m:
        pytest.skip("No single-fraction simplification pattern found")
    a, b = int(m.group(1)), int(m.group(2))
    expected = Fraction(a, b)  # Fraction auto-reduces
    stated = _parse_fraction(q.get("correct_answer", ""))
    assert stated is not None, (
        f"[{q['_source']}] Could not parse correct_answer {q.get('correct_answer')!r}"
    )
    assert stated == expected, (
        f"[{q['_source']}] Simplified {a}/{b} = {expected}, "
        f"but correct_answer is {stated} ({q.get('correct_answer')!r})"
    )


@pytest.mark.parametrize("q", ALL_QUESTIONS, ids=_question_id)
def test_denominator_conversion_arithmetic(q):
    """'Equivalent to N/D expressed with denominator T': answer must equal N/D and use denominator T."""
    qt = q.get("question_text", "")
    m = _DENOM_CONV_PAT.search(qt)
    if not m:
        pytest.skip("No denominator-conversion pattern found")
    num, den, target_den = int(m.group(1)), int(m.group(2)), int(m.group(3))
    expected_value = Fraction(num, den)
    stated = _parse_fraction(q.get("correct_answer", ""))
    assert stated is not None, (
        f"[{q['_source']}] Could not parse correct_answer {q.get('correct_answer')!r}"
    )
    assert stated == expected_value, (
        f"[{q['_source']}] {num}/{den} ≡ {expected_value}, "
        f"but correct_answer is {stated} ({q.get('correct_answer')!r})"
    )
    # Also verify the answer uses the target denominator
    raw = q.get("correct_answer", "")
    m_den = re.search(r"(\d+)\s*/\s*(\d+)", raw)
    if m_den:
        assert int(m_den.group(2)) == target_den, (
            f"[{q['_source']}] Answer denominator should be {target_den} "
            f"but got {m_den.group(2)} in {raw!r}"
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
        qt = q.get("question_text", "")
        stated = _parse_fraction(correct)

        if correct not in opts:
            errors.append(f"[{src}|{qid}] correct_answer {correct!r} not in options {opts}")

        if ci is not None:
            if not (0 <= ci < len(opts)):
                errors.append(f"[{src}|{qid}] correct_index={ci} out of range")
            elif opts[ci] != correct:
                errors.append(f"[{src}|{qid}] options[{ci}]={opts[ci]!r} != correct_answer={correct!r}")

        # LaTeX inline addition (\frac or \dfrac)
        m = _LATEX_ADD_PAT.search(qt)
        if m:
            a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            expected = Fraction(a, b) + Fraction(c, d)
            if stated is not None and stated != expected:
                errors.append(f"[{src}|{qid}] LaTeX add {a}/{b}+{c}/{d}={expected} but answer={stated} ({correct!r})")

        # Verbal addition
        m = _VERBAL_ADD_PAT.search(qt)
        if m:
            a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            expected = Fraction(a, b) + Fraction(c, d)
            if stated is not None and stated != expected:
                errors.append(f"[{src}|{qid}] Verbal add {a}/{b}+{c}/{d}={expected} but answer={stated} ({correct!r})")

        # LaTeX inline subtraction (\frac or \dfrac)
        m = _LATEX_SUB_PAT.search(qt)
        if m:
            a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            expected = Fraction(a, b) - Fraction(c, d)
            if stated is not None and stated != expected:
                errors.append(f"[{src}|{qid}] LaTeX sub {a}/{b}-{c}/{d}={expected} but answer={stated} ({correct!r})")

        # Verbal subtraction: "subtracting A from B" → B - A
        m = _VERBAL_SUB_PAT.search(qt)
        if m:
            a, b, c, d = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            expected = Fraction(c, d) - Fraction(a, b)
            if stated is not None and stated != expected:
                errors.append(f"[{src}|{qid}] Verbal sub {c}/{d}-{a}/{b}={expected} but answer={stated} ({correct!r})")

        # Simplification
        if not _OP_KEYWORD_PAT.search(qt) and not _FRAC_OP_PAT.search(qt):
            m = _SIMPLIFY_PAT.search(qt)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                expected = Fraction(a, b)
                if stated is not None and stated != expected:
                    errors.append(f"[{src}|{qid}] Simplify {a}/{b}={expected} but answer={stated} ({correct!r})")

        # Denominator conversion
        m = _DENOM_CONV_PAT.search(qt)
        if m:
            num, den, target_den = int(m.group(1)), int(m.group(2)), int(m.group(3))
            expected_value = Fraction(num, den)
            if stated is not None and stated != expected_value:
                errors.append(f"[{src}|{qid}] Denom conv {num}/{den}≡{expected_value} but answer={stated} ({correct!r})")
            raw_m = re.search(r"(\d+)\s*/\s*(\d+)", correct)
            if raw_m and int(raw_m.group(2)) != target_den:
                errors.append(f"[{src}|{qid}] Denom conv answer {correct!r} should use denominator {target_den}")

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
