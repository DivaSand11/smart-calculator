"""
main.py
Entry point for the Scientific Calculator with Smart Suggestions.
Run with: python main.py
"""

from db.database import init_db
from ui.main_window import CalculatorApp


def main():
    init_db()
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
