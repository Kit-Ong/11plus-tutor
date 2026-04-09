# Importing Custom Questions

## Data Flow Overview

```
JSON files ──► import_questions.py ──► elevenplustutor.db ◄── app reads at runtime
CSV review ──► validate_questions.py ──┘
```

The app only reads from `elevenplustutor.db` at runtime. The JSON files and CSV are upstream sources used to populate it.

---

## The Three Files

### `elevenplustutor.db`
The live SQLite database the running app reads from. Editing this takes effect immediately without a restart. Contains a `questions` table with one row per question.

### `data/questions/**/*.json`
Source question files produced by the AI generator (or written manually). The import script reads these and inserts any new questions into the DB, skipping ones that already exist (matched by `id`). Stored under subject/topic subfolders, e.g.:
```
data/questions/mathematics/fractions/f90f1f5b-....json
data/questions/verbal_reasoning/synonyms/abc123-....json
```

### `question_review/*.csv`
Human-review exports. Each CSV covers one question type and includes `VERIFIED (Y/N)` and `ISSUES/NOTES` columns. After marking corrections, run `validate_questions.py --import-review` to write changes back to the DB.

---

## Import Options

### Option A — Single JSON file (recommended for one or a few questions)

1. Create a `.json` file anywhere under `data/questions/`:

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "exam_type": "11plus_gl",
  "subject": "mathematics",
  "question_type": "fractions",
  "difficulty": 2,
  "question_text": "What is \\(\\frac{1}{2} + \\frac{1}{4}\\)?",
  "options": [
    "\\(\\frac{3}{4}\\)",
    "\\(\\frac{1}{6}\\)",
    "\\(\\frac{2}{6}\\)",
    "\\(\\frac{1}{3}\\)"
  ],
  "correct_answer": "\\(\\frac{3}{4}\\)",
  "correct_index": 0,
  "explanation": "Convert to a common denominator of 4: \\(\\frac{2}{4} + \\frac{1}{4} = \\frac{3}{4}\\)."
}
```

2. Run the importer from the project root:

```bash
python scripts/import_questions.py
```

The script walks all subfolders under `data/questions/`, importing every `.json` file. Questions whose `id` already exists in the DB are silently skipped.

> **Tip**: Generate a UUID with `python -c "import uuid; print(uuid.uuid4())"`.

---

### Option B — Bulk JSON (many questions at once)

Place a JSON **array** at `data/questions/all_questions.json`. The importer checks this file first before scanning subfolders:

```json
[
  {
    "id": "...",
    "subject": "mathematics",
    ...
  },
  {
    "id": "...",
    "subject": "verbal_reasoning",
    ...
  }
]
```

Then run:

```bash
python scripts/import_questions.py
```

---

### Option C — Edit the database directly (quick fixes only)

For small corrections to existing questions (e.g. fixing a wrong answer):

```bash
python - <<'EOF'
import sqlite3, json

conn = sqlite3.connect('elevenplustutor.db')

# Example: fix correct_answer and options for a specific question
conn.execute("""
    UPDATE questions
    SET correct_answer = ?, options = ?, correct_index = ?
    WHERE id = ?
""", (
    r'\(\frac{5}{8}\)',
    json.dumps([r'\(\frac{5}{8}\)', r'\(\frac{1}{2}\)', r'\(\frac{5}{12}\)', r'\(\frac{3}{4}\)']),
    0,
    'f90f1f5b-a846-4d61-9eab-1e805d150141'
))

conn.commit()
conn.close()
print("Done")
EOF
```

> **Note**: Direct DB edits are not reflected back in the JSON source files or CSV review sheets. Update those manually if you want the fix to survive a full re-import.

---

## Required JSON Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string (UUID) | Yes | Must be unique |
| `exam_type` | string | Yes | e.g. `11plus_gl`, `11plus_cem`, `gcse` |
| `subject` | string | Yes | e.g. `mathematics`, `verbal_reasoning`, `english` |
| `question_type` | string | Yes | e.g. `fractions`, `synonyms`, `code_words` |
| `difficulty` | integer 1–5 | Yes | 1 = easiest, 5 = hardest |
| `question_text` | string | Yes | Supports LaTeX via `\(...\)` or `$$...$$` |
| `options` | array of strings | Yes | Multiple-choice options |
| `correct_answer` | string | Yes | Must exactly match one of `options` |
| `correct_index` | integer | Yes | 0-based index of the correct option |
| `explanation` | string | No | Worked solution shown after answering |
| `hint` | string | No | Optional hint shown on request |
| `marks_available` | integer | No | Defaults to 1 |

---

## LaTeX Formatting in Questions

Use `\(...\)` for inline math and `\[...\]` for block math. The frontend converts these automatically.

```json
"question_text": "What is \\(\\frac{3}{8} + \\frac{1}{4}\\)?"
"options": ["\\(\\frac{5}{8}\\)", "\\(\\frac{1}{2}\\)"]
```

Bare `\frac{a}{b}` (without wrappers) is also supported but `\(...\)` is preferred for consistency.

---

## After Importing

Verify the import worked:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('elevenplustutor.db')
row = conn.execute('SELECT COUNT(*) FROM questions').fetchone()
print(f'Total questions in DB: {row[0]}')
conn.close()
"
```

To export all questions to CSV for review:

```bash
python scripts/validate_questions.py --export
```
