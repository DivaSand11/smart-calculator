# Scientific Calculator with Smart Suggestions

A desktop scientific calculator (Tkinter) that persists calculation history in
SQLite and suggests relevant formulas/methods as you type, using keyword
pattern matching against a curated formula bank.

## Tech Stack
- **Python 3** — core logic
- **SQLite** — persistent calculation history
- **Tkinter** — desktop GUI
- **Keyword matching** (rule-based, not a trained NLP model) — suggestion engine

## Features
- Safe expression evaluator (whitelisted `math` functions only — no raw `eval` with full Python access)
- Scientific functions: trig, log, sqrt, factorial, degrees/radians, etc.
- Persistent history: every calculation is saved with timestamp and (if matched) the formula method used
- Search/filter history, recall/reload a past calculation with a double-click, export history to CSV
- Smart suggestion panel: type "hypotenuse" or "compound interest" and get the matching formula + a ready-to-run example

## Project Structure
```
scientific_calculator/
├── main.py                 # Entry point
├── calculator_engine.py    # Safe math evaluation
├── suggestion_engine.py    # Keyword -> formula matching
├── db/
│   ├── database.py         # SQLite connection + schema
│   └── history_dao.py      # CRUD for history table
├── ui/
│   └── main_window.py      # Tkinter GUI
├── data/
│   └── keyword_map.json    # Formula bank (16 common formulas)
└── README.md
```

## Setup & Run

1. Requires Python 3.8+.
2. Tkinter ships with most Python installers on Windows/macOS. On Linux, if you get a `ModuleNotFoundError: No module named 'tkinter'`, install it:
   ```bash
   sudo apt install python3-tk
   ```
3. No third-party pip packages needed — everything uses the standard library.
4. Run:
   ```bash
   cd scientific_calculator
   python main.py
   ```
   This auto-creates `calculator.db` (SQLite file) on first run.

## Try These
- Type `sqrt(3^2+4^2)` and press Enter → `5`
- Type "hypotenuse" in the box → suggestion panel shows the Pythagorean theorem, double-click it to auto-fill the example
- Type "compound interest" → shows `A = P * (1 + r/n)^(n*t)` with a worked example
- Double-click any row in the history panel to reload that expression

## Design Notes (useful for interviews)
- **Layered architecture**: UI never touches SQL or math directly — it calls `calculator_engine`, `suggestion_engine`, and `db.history_dao`. Swapping Tkinter for a web frontend later would only mean rewriting the UI layer.
- **Security**: expressions are evaluated with `eval()` restricted to an empty `__builtins__` and a whitelist dict of safe math functions — prevents arbitrary code execution from user input.
- **Suggestion engine**: honestly framed as keyword/pattern matching over a formula bank, with stopword filtering and phrase-vs-token scoring — not a trained NLP model. It's transparent, fast, and easy to extend by adding entries to `keyword_map.json`.

## Possible Extensions
- Add a "favorites" star for frequently reused calculations
- Graph plotting for functions (matplotlib)
- Swap the keyword matcher for a small TF-IDF or embedding-based matcher for fuzzier suggestions
- Package as a `.exe`/`.app` with PyInstaller
