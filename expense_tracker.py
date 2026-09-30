"""
Simple expense tracker.

Row 1 is the starting balance. Rows 2 onwards: A = amount, B = expense name.
Each expense is subtracted from the balance.

Run it with:  python expense_tracker.py
"""

import json
import tkinter as tk
from pathlib import Path

SAVE_FILE = Path(__file__).with_name("expenses.json")

rows = []  # each item is (amount_box, name_box, balance_label)


def is_valid_amount(text):
    """Allow only an empty box or a number that is not negative."""
    if text == "":
        return True
    if "-" in text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def to_number(text):
    try:
        return float(text)
    except ValueError:
        return 0.0


def add_row(amount="", name=""):
    row_number = len(rows) + 2
    table_row = row_number  # grid row 0 is the header, grid row 1 is row 1

    tk.Label(table, text=row_number).grid(row=table_row, column=0)
    amount_box = tk.Entry(table, width=12, validate="key", validatecommand=check_amount)
    amount_box.grid(row=table_row, column=1)
    name_box = tk.Entry(table, width=25)
    name_box.grid(row=table_row, column=2)
    balance_label = tk.Label(table, width=12, anchor="e")
    balance_label.grid(row=table_row, column=3)

    amount_box.insert(0, amount)
    name_box.insert(0, name)
    rows.append((amount_box, name_box, balance_label))


def update(event=None):
    balance = to_number(start_box.get())
    start_label.config(text=f"{balance:.2f}")
    for amount_box, name_box, balance_label in rows:
        balance = balance - to_number(amount_box.get())
        balance_label.config(text=f"{balance:.2f}")
    remaining_label.config(text=f"Remaining balance: {balance:.2f}")
    save()


def save():
    data = {
        "start": start_box.get(),
        "expenses": [[a.get(), n.get()] for a, n, _ in rows],
    }
    SAVE_FILE.write_text(json.dumps(data))


def load():
    if SAVE_FILE.exists():
        data = json.loads(SAVE_FILE.read_text())
        start_box.delete(0, "end")
        start_box.insert(0, data["start"])
        for amount, name in data["expenses"]:
            add_row(amount, name)
    if not rows:
        add_row()
    update()


def add_row_clicked():
    add_row()
    update()


window = tk.Tk()
window.title("Expense Tracker")
check_amount = (window.register(is_valid_amount), "%P")

table = tk.Frame(window, padx=10, pady=10)
table.pack()

# Header
for column, title in enumerate(["#", "A: Amount", "B: Expense name", "Balance"]):
    tk.Label(table, text=title, font=("Arial", 10, "bold")).grid(row=0, column=column)

# Row 1: starting balance
tk.Label(table, text="1").grid(row=1, column=0)
start_box = tk.Entry(table, width=12, validate="key", validatecommand=check_amount)
start_box.insert(0, "1000")
start_box.grid(row=1, column=1)
tk.Label(table, text="Starting balance", anchor="w").grid(row=1, column=2, sticky="w")
start_label = tk.Label(table, width=12, anchor="e")
start_label.grid(row=1, column=3)

tk.Button(window, text="+ Add expense", command=add_row_clicked).pack()
remaining_label = tk.Label(window, font=("Arial", 11, "bold"), pady=10)
remaining_label.pack()

window.bind_all("<KeyRelease>", update)

load()
window.mainloop()
