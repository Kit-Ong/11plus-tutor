"""Analyse what the skipped tests cover"""
import sqlite3
import re
from fractions import Fraction

conn = sqlite3.connect('elevenplustutor.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT id, question_text, correct_answer, options FROM questions WHERE question_type=?', ('fractions',))
rows = [dict(r) for r in cur.fetchall()]
conn.close()

import json
for r in rows:
    r['options'] = json.loads(r['options'])

add_pat = re.compile(r'frac\{\d+\}\{\d+\}[^a-zA-Z0-9]*\+[^a-zA-Z0-9]*frac\{\d+\}\{\d+\}')
sub_pat = re.compile(r'frac\{\d+\}\{\d+\}[^a-zA-Z0-9]*-[^a-zA-Z0-9]*frac\{\d+\}\{\d+\}')

print("=== SKIP test_addition_arithmetic (no LaTeX add pattern matched) ===")
for r in rows:
    if not add_pat.search(r['question_text']):
        cat = []
        if '+' in r['question_text']: cat.append('has +')
        if '-' in r['question_text']: cat.append('has -')
        if 'frac' not in r['question_text']: cat.append('NO FRAC')
        print(f"  ID: {r['id']}")
        print(f"  Q: {r['question_text'][:130]}")
        print(f"  Correct: {r['correct_answer']}")
        print(f"  Notes: {', '.join(cat) if cat else 'no operation'}")
        print()

print()
print("=== SKIP test_subtraction_arithmetic (no LaTeX subtract pattern matched) ===")
for r in rows:
    if not sub_pat.search(r['question_text']):
        # only list the ones that ARE subtraction (i.e. have minus) but pattern doesn't catch
        if '-' not in r['question_text']:
            continue
        print(f"  ID: {r['id']}")
        print(f"  Q: {r['question_text'][:130]}")
        print()
