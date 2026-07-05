"""
suggestion_engine.py
Keyword-pattern-matching "smart suggestions" layer.

NOTE: This is deliberately simple keyword/pattern matching, not a trained
NLP model. It tokenizes the user's query, scores each known formula entry
by how many of its keywords overlap with the query, and returns the
best matches ranked by score. This is intentional and easy to explain
in an interview: transparent, fast, no external dependencies, and good
enough for a bounded domain like "common formulas."
"""

import json
import os
import re
from typing import List, Dict

_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "keyword_map.json")

with open(_DATA_PATH, "r", encoding="utf-8") as f:
    _FORMULA_BANK: List[Dict] = json.load(f)

# Common words filtered out so they don't create false-positive keyword overlaps
_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "for", "to", "is", "are", "with",
    "and", "or", "how", "much", "will", "my", "find", "what", "calculate",
    "i", "me", "do", "does", "can", "you", "please", "get", "value", "solve"
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


def _score_entry(query_tokens: List[str], entry: Dict) -> int:
    """Score = number of keyword matches (phrase overlap or token overlap)."""
    query_set = set(query_tokens)
    score = 0
    for kw in entry["keywords"]:
        kw_tokens = [t for t in kw.lower().split() if t not in _STOPWORDS]
        if not kw_tokens:
            continue
        overlap = set(kw_tokens) & query_set
        if len(overlap) == len(kw_tokens):
            # every meaningful word in the keyword phrase is present -> strong signal
            score += len(kw_tokens) * 2
        else:
            score += len(overlap)
    return score


def get_suggestions(query: str, top_n: int = 3) -> List[Dict]:
    """
    Given a natural-language-ish query (e.g. "hypotenuse of right triangle"),
    return the top_n matching formula suggestions, best first.
    Returns an empty list if nothing scores above zero.
    """
    if not query or not query.strip():
        return []

    tokens = _tokenize(query)
    scored = []
    for entry in _FORMULA_BANK:
        score = _score_entry(tokens, entry)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in scored[:top_n]]


if __name__ == "__main__":
    tests = [
        "find the hypotenuse of a right triangle",
        "area of a circle with radius 5",
        "how much will my investment grow with compound interest",
        "roots of a quadratic equation",
        "random gibberish text",
    ]
    for q in tests:
        print(f"\nQuery: {q}")
        for s in get_suggestions(q):
            print(f"  -> [{s['method']}] {s['formula']}  (e.g. {s['example']})")
        if not get_suggestions(q):
            print("  -> No suggestions found.")
