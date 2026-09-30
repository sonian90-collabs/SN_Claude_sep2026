"""
Expense Tracker - a small Excel-style spreadsheet written in Python.

Column A = amount, column B = expense name, column C = balance (calculated).
Row 1 holds the starting balance. Every row after that is an expense
that gets subtracted from the balance.

Run it with:  python expense_tracker.py
"""

import json
import tkinter as tk
from pathlib import Path

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

SAVE_FILE = Path(__file__).with_name("expenses.json")  # where data is saved
STARTING_BALANCE = "1000"
START_ROWS = 25              # how many rows the sheet shows at first

# Excel-like colors
EXCEL_GREEN = "#217346"
GRID_LINE = "#d4d4d4"
HEADER_BG = "#f3f3f3"
HEADER_SELECTED_BG = "#d3f0e0"
SELECTED_BORDER = "#107c41"
NEGATIVE_RED = "#c00000"
FONT = ("Calibri", 11)
HEADER_FONT = ("Calibri", 11)

# Column letter -> (title shown in the name box, width in characters)
COLUMNS = {
    "A": ("Amount", 14),
    "B": ("Expense name", 30),
    "C": ("Balance", 14),
}


class ExpenseSheet:
    def __init__(self, root):
        self.root = root
        root.title("Expense Tracker - Excel style")
        root.geometry("760x560")
        root.configure(bg="white")

        # self.cells[row][column_letter] -> the Entry widget for that cell
        self.cells = {}
        self.row_labels = {}
        self.col_labels = {}
        self.selected = (1, "A")

        self.build_ribbon()
        self.build_formula_bar()
        self.build_grid()
        self.build_status_bar()

        self.load()
        self.select_cell(1, "A")

    # -----------------------------------------------------------------------
    # Building the window
    # -----------------------------------------------------------------------

    def build_ribbon(self):
        """The green title bar across the top, like Excel."""
        ribbon = tk.Frame(self.root, bg=EXCEL_GREEN, height=36)
        ribbon.pack(fill="x")
        tk.Label(ribbon, text="  Expense Tracker", bg=EXCEL_GREEN, fg="white",
                 font=("Calibri", 13, "bold")).pack(side="left", pady=6)
        tk.Button(ribbon, text="+ Add rows", command=self.add_more_rows,
                  bg="white", fg=EXCEL_GREEN, relief="flat",
                  font=FONT).pack(side="right", padx=8, pady=4)

    def build_formula_bar(self):
        """The 'name box' (shows e.g. A2) and the formula bar (shows the value)."""
        bar = tk.Frame(self.root, bg="white", pady=4)
        bar.pack(fill="x", padx=4)

        self.name_box = tk.Label(bar, width=8, bg="white", relief="solid", bd=1,
                                 font=FONT, anchor="w")
        self.name_box.pack(side="left")

        tk.Label(bar, text=" fx ", bg="white", fg="#666",
                 font=("Calibri", 11, "italic")).pack(side="left")

        self.formula_text = tk.StringVar()
        tk.Entry(bar, textvariable=self.formula_text, relief="solid", bd=1,
                 font=FONT, state="readonly",
                 readonlybackground="white").pack(side="left", fill="x", expand=True)

    def build_grid(self):
        """The spreadsheet itself, inside a scrollable area."""
        holder = tk.Frame(self.root, bg="white")
        holder.pack(fill="both", expand=True)

        canvas = tk.Canvas(holder, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(holder, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # The grid lines are just the GRID_LINE background showing through
        # 1-pixel gaps between the cells.
        self.grid = tk.Frame(canvas, bg=GRID_LINE)
        canvas.create_window((0, 0), window=self.grid, anchor="nw")
        self.grid.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # Mouse wheel scrolling (Windows/Mac use <MouseWheel>, Linux uses buttons 4/5)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        self.canvas = canvas

        # Top-left corner box, then the A, B, C column headers
        tk.Label(self.grid, bg=HEADER_BG, width=4).grid(row=0, column=0, padx=(0, 1), pady=(0, 1), sticky="nsew")
        for i, (letter, (_, width)) in enumerate(COLUMNS.items(), start=1):
            label = tk.Label(self.grid, text=letter, bg=HEADER_BG, font=HEADER_FONT, width=width)
            label.grid(row=0, column=i, padx=(0, 1), pady=(0, 1), sticky="nsew")
            self.col_labels[letter] = label

        self.row_count = 0
        self.add_more_rows(START_ROWS)

    def build_status_bar(self):
        """Sheet tab and totals at the bottom, like Excel's status bar."""
        bottom = tk.Frame(self.root, bg=HEADER_BG)
        bottom.pack(fill="x", side="bottom")
        tk.Label(bottom, text=" Sheet1 ", bg="white", fg=EXCEL_GREEN,
                 font=("Calibri", 11, "bold"), relief="solid", bd=1).pack(side="left", padx=6, pady=3)

        self.status = tk.Label(bottom, bg=HEADER_BG, font=FONT)
        self.status.pack(side="right", padx=10)

    # -----------------------------------------------------------------------
    # Rows and cells
    # -----------------------------------------------------------------------

    def add_more_rows(self, how_many=10):
        """Add empty rows to the bottom of the sheet."""
        for _ in range(how_many):
            self.row_count += 1
            row = self.row_count

            number = tk.Label(self.grid, text=str(row), bg=HEADER_BG, font=HEADER_FONT, width=4)
            number.grid(row=row, column=0, padx=(0, 1), pady=(0, 1), sticky="nsew")
            self.row_labels[row] = number

            self.cells[row] = {}
            for i, (letter, (_, width)) in enumerate(COLUMNS.items(), start=1):
                cell = tk.Entry(self.grid, width=width, font=FONT, relief="flat", bd=2,
                                highlightthickness=2, highlightcolor=SELECTED_BORDER,
                                highlightbackground="white")
                cell.grid(row=row, column=i, padx=(0, 1), pady=(0, 1), sticky="nsew")

                if letter == "A":
                    cell.configure(justify="right")  # numbers line up on the right
                if letter == "C":
                    # Balance is calculated, so the user can't type in it
                    cell.configure(justify="right", state="readonly",
                                   readonlybackground="white")

                # When a cell is clicked/focused, remember it as "selected"
                cell.bind("<FocusIn>", lambda e, r=row, c=letter: self.select_cell(r, c))
                # Recalculate whenever something is typed
                cell.bind("<KeyRelease>", lambda e: self.recalculate())
                # Excel-style keyboard movement
                cell.bind("<Return>", lambda e, r=row, c=letter: self.move(r, c, 1, 0))
                cell.bind("<Down>", lambda e, r=row, c=letter: self.move(r, c, 1, 0))
                cell.bind("<Up>", lambda e, r=row, c=letter: self.move(r, c, -1, 0))
                cell.bind("<Tab>", lambda e, r=row, c=letter: self.move(r, c, 0, 1))
                cell.bind("<Shift-Tab>", lambda e, r=row, c=letter: self.move(r, c, 0, -1))
                self.cells[row][letter] = cell

    def move(self, row, letter, down, right):
        """Move the selection like Enter / Tab / arrow keys do in Excel."""
        letters = list(COLUMNS)
        col_index = max(0, min(len(letters) - 1, letters.index(letter) + right))
        new_row = max(1, row + down)
        if new_row > self.row_count:
            self.add_more_rows()
        self.cells[new_row][letters[col_index]].focus_set()
        return "break"  # stop tkinter's default key behavior

    def select_cell(self, row, letter):
        """Highlight the selected cell's row number and column letter."""
        old_row, old_letter = self.selected
        self.row_labels[old_row].configure(bg=HEADER_BG, fg="black")
        self.col_labels[old_letter].configure(bg=HEADER_BG, fg="black")

        self.selected = (row, letter)
        self.row_labels[row].configure(bg=HEADER_SELECTED_BG, fg=EXCEL_GREEN)
        self.col_labels[letter].configure(bg=HEADER_SELECTED_BG, fg=EXCEL_GREEN)

        self.name_box.configure(text=f" {letter}{row}")
        self.update_formula_bar()

    def update_formula_bar(self):
        row, letter = self.selected
        self.formula_text.set(self.cells[row][letter].get())

    def get(self, row, letter):
        return self.cells[row][letter].get().strip()

    def set_balance(self, row, text, negative=False):
        """Write into a column C cell (which is normally read-only)."""
        cell = self.cells[row]["C"]
        cell.configure(state="normal")
        cell.delete(0, "end")
        cell.insert(0, text)
        cell.configure(state="readonly", fg=NEGATIVE_RED if negative else "black")

    # -----------------------------------------------------------------------
    # The math
    # -----------------------------------------------------------------------

    def recalculate(self):
        """Start from A1 and subtract every amount in A2, A3, A4, ..."""
        balance = to_number(self.get(1, "A"))
        total_spent = 0.0
        self.set_balance(1, f"{balance:,.2f}")

        for row in range(2, self.row_count + 1):
            amount_text = self.get(row, "A")
            if amount_text == "" and self.get(row, "B") == "":
                self.set_balance(row, "")  # empty row: show nothing
                continue

            amount = to_number(amount_text)
            balance -= amount
            total_spent += amount
            self.set_balance(row, f"{balance:,.2f}", negative=balance < 0)

        self.status.configure(
            text=f"Total spent: {total_spent:,.2f}      Remaining balance: {balance:,.2f}",
            fg=NEGATIVE_RED if balance < 0 else "black",
        )
        self.update_formula_bar()
        self.save()

    # -----------------------------------------------------------------------
    # Saving and loading
    # -----------------------------------------------------------------------

    def save(self):
        """Save column A and B values to expenses.json."""
        rows = []
        for row in range(1, self.row_count + 1):
            rows.append([self.get(row, "A"), self.get(row, "B")])
        # Drop empty rows at the end so the file stays small
        while rows and rows[-1] == ["", ""]:
            rows.pop()
        SAVE_FILE.write_text(json.dumps(rows, indent=2))

    def load(self):
        """Load saved data, or fill in the starting balance the first time."""
        if SAVE_FILE.exists():
            rows = json.loads(SAVE_FILE.read_text())
        else:
            rows = [[STARTING_BALANCE, "Starting balance"]]

        if len(rows) > self.row_count:
            self.add_more_rows(len(rows) - self.row_count + 5)

        for row, (amount, name) in enumerate(rows, start=1):
            self.cells[row]["A"].insert(0, amount)
            self.cells[row]["B"].insert(0, name)
        self.recalculate()


def to_number(text):
    """Turn text like '1,250.50' into a number. Anything invalid counts as 0."""
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return 0.0


if __name__ == "__main__":
    window = tk.Tk()
    ExpenseSheet(window)
    window.mainloop()
