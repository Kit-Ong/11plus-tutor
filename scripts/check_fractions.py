"""Check fractions questions for arithmetic errors"""
import sqlite3
import json
from fractions import Fraction
import re
import sys

DB_PATH = "elevenplustutor.db"

def extract_fraction(s):
    """Extract a Fraction from a string like '5/8', '\\frac{5}{8}', '\\(\\frac{5}{8}\\)'"""
    s = s.strip()
    # Plain fraction like 5/8
    m = re.search(r'(\d+)/(\d+)', s)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    # LaTeX \frac{n}{d}
    m = re.search(r'\\frac\{(\d+)\}\{(\d+)\}', s)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    return None

def check_db_questions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, question_text, options, correct_answer, worked_solution FROM questions WHERE question_type='fractions'")
    rows = cur.fetchall()
    print(f"Total fractions questions in DB: {len(rows)}")

    issues = []
    for r in rows:
        opts = json.loads(r['options']) if r['options'] else []
        correct = r['correct_answer'] or ''
        # Issue 1: correct_answer not in options
        if correct not in opts:
            issues.append({
                'id': r['id'],
                'issue': 'correct_answer_not_in_options',
                'question': r['question_text'][:120],
                'correct': correct,
                'options': opts,
                'worked_solution': (r['worked_solution'] or '')[:200],
            })
    print(f"Questions where correct_answer not in options: {len(issues)}")
    for issue in issues:
        print(f"  ID: {issue['id']}")
        print(f"  Q:  {issue['question']}")
        print(f"  Correct: {issue['correct']}")
        print(f"  Options: {issue['options']}")
        print()

    conn.close()
    return issues

def check_json_questions():
    import glob, os
    issues = []
    for f in glob.glob('data/questions/mathematics/fractions/*.json'):
        with open(f) as fh:
            q = json.load(fh)
        opts = q.get('options', [])
        correct = q.get('correct_answer', '')
        if correct not in opts:
            issues.append({
                'id': q.get('id'),
                'file': os.path.basename(f),
                'issue': 'correct_answer_not_in_options',
                'question': q.get('question_text', '')[:120],
                'correct': correct,
                'options': opts,
            })
    print(f"\nJSON question files with correct_answer not in options: {len(issues)}")
    for issue in issues:
        print(f"  File: {issue['file']}")
        print(f"  Q:    {issue['question']}")
        print(f"  Correct: {issue['correct']}")
        print(f"  Options: {issue['options']}")
    return issues

if __name__ == "__main__":
    check_db_questions()
    check_json_questions()
