"""
main_window.py
Tkinter GUI for the Scientific Calculator with Smart Suggestions.

UI is intentionally kept free of math/DB logic — it only calls into
calculator_engine, suggestion_engine, and db.history_dao.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import calculator_engine as calc
import suggestion_engine as suggest
from db import history_dao


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Calculator — Smart Suggestions")
        self.geometry("880x560")
        self.minsize(760, 480)
        self.configure(bg="#1e1e2e")

        self._build_layout()
        self._refresh_history()

    # ------------------------------------------------------------------ UI
    def _build_layout(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Calc.TButton", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", rowheight=26, font=("Consolas", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_calculator_panel(left)
        self._build_suggestion_panel(left)
        self._build_history_panel(right)

    def _build_calculator_panel(self, parent):
        ttk.Label(parent, text="Expression", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.expr_var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=self.expr_var, font=("Consolas", 16))
        entry.pack(fill="x", pady=(2, 8))
        entry.bind("<Return>", lambda e: self.calculate())
        entry.bind("<KeyRelease>", lambda e: self._update_suggestions())
        entry.focus_set()

        self.result_var = tk.StringVar(value="Result: —")
        ttk.Label(parent, textvariable=self.result_var, font=("Segoe UI", 14, "bold"),
                  foreground="#2e7d32").pack(anchor="w", pady=(0, 10))

        # Button grid (basic scientific calculator pad)
        pad = ttk.Frame(parent)
        pad.pack(fill="both", expand=True)

        buttons = [
            ["7", "8", "9", "/", "sqrt("],
            ["4", "5", "6", "*", "^"],
            ["1", "2", "3", "-", "log("],
            ["0", ".", "(", ")", "+"],
            ["sin(", "cos(", "tan(", "pi", "e"],
            ["C", "⌫", "=", "", ""],
        ]
        for r, row in enumerate(buttons):
            pad.rowconfigure(r, weight=1)
            for c, label in enumerate(row):
                pad.columnconfigure(c, weight=1)
                if not label:
                    continue
                btn = ttk.Button(pad, text=label, style="Calc.TButton",
                                  command=lambda l=label: self._on_button(l))
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Export History to CSV", command=self._export_csv).pack(side="left")
        ttk.Button(actions, text="Clear History", command=self._clear_history).pack(side="left", padx=8)

    def _build_suggestion_panel(self, parent):
        ttk.Label(parent, text="Smart Suggestions (based on your input)",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(14, 2))
        self.suggestion_box = tk.Listbox(parent, height=5, font=("Consolas", 10))
        self.suggestion_box.pack(fill="x")
        self.suggestion_box.bind("<Double-Button-1>", self._apply_suggestion)
        self._current_suggestions = []

    def _build_history_panel(self, parent):
        ttk.Label(parent, text="Calculation History", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", pady=(4, 6))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<Return>", lambda e: self._refresh_history())
        ttk.Button(search_frame, text="Search", command=self._refresh_history).pack(side="left", padx=(6, 0))

        columns = ("expression", "result", "method", "timestamp")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)
        for col, label, width in [
            ("expression", "Expression", 140),
            ("result", "Result", 80),
            ("method", "Method", 110),
            ("timestamp", "Time", 130),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-Button-1>", self._recall_history_item)

        ttk.Label(parent, text="(Double-click a row to reload that calculation)",
                  font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------- actions
    def _on_button(self, label: str):
        if label == "C":
            self.expr_var.set("")
        elif label == "⌫":
            self.expr_var.set(self.expr_var.get()[:-1])
        elif label == "=":
            self.calculate()
        else:
            self.expr_var.set(self.expr_var.get() + label)
        self._update_suggestions()

    def calculate(self):
        expr = self.expr_var.get()
        try:
            result = calc.evaluate(expr)
            formatted = calc.format_result(result)
            self.result_var.set(f"Result: {formatted}")

            method = self._current_suggestions[0]["method"] if self._current_suggestions else None
            history_dao.add_entry(expr, formatted, method)
            self._refresh_history()
        except calc.CalculationError as e:
            self.result_var.set("Result: Error")
            messagebox.showerror("Calculation Error", str(e))

    def _update_suggestions(self):
        query = self.expr_var.get()
        self._current_suggestions = suggest.get_suggestions(query)
        self.suggestion_box.delete(0, tk.END)
        if not self._current_suggestions:
            self.suggestion_box.insert(tk.END, "No suggestions — type a math term (e.g. 'hypotenuse')")
            return
        for s in self._current_suggestions:
            self.suggestion_box.insert(tk.END, f"[{s['method']}] {s['formula']}  →  e.g. {s['example']}")

    def _apply_suggestion(self, event):
        selection = self.suggestion_box.curselection()
        if not selection or not self._current_suggestions:
            return
        idx = selection[0]
        if idx < len(self._current_suggestions):
            self.expr_var.set(self._current_suggestions[idx]["example"])

    def _refresh_history(self):
        self.tree.delete(*self.tree.get_children())
        keyword = self.search_var.get().strip()
        rows = history_dao.search(keyword) if keyword else history_dao.get_all()
        for row in rows:
            self.tree.insert("", tk.END, iid=row["id"], values=(
                row["expression"], row["result"], row["method_used"] or "—", row["timestamp"]
            ))

    def _recall_history_item(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        expression = item["values"][0]
        self.expr_var.set(expression)
        self._update_suggestions()

    def _clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all calculation history?"):
            history_dao.clear_all()
            self._refresh_history()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
        if path:
            history_dao.export_csv(path)
            messagebox.showinfo("Exported", f"History exported to:\n{path}")


if __name__ == "__main__":
    from db.database import init_db
    init_db()
    app = CalculatorApp()
    app.mainloop()
