"""
Personal Utility Expense Tracker
Uses SQLite for persistent storage.
"""

import sqlite3
import datetime
import os

# Always store the DB next to this script file, regardless of where Python is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "expenses.db")


# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def init_db():
    """Create the expenses table if it doesn't already exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CORE DATA FUNCTIONS
# ─────────────────────────────────────────────

def load_expenses():
    """Return all expenses as a list of dicts, newest first."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_expense(date, amount, category, description):
    """Insert a single expense record into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
        (date, amount, category, description)
    )
    conn.commit()
    conn.close()


def load_expenses_for_date(date_str):
    """Return all expenses for a specific date (YYYY-MM-DD)."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE date = ? ORDER BY id ASC",
        (date_str,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def load_all_dates():
    """Return a sorted list of all unique dates that have expenses."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM expenses ORDER BY date DESC")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dates


# ─────────────────────────────────────────────
# FEATURE FUNCTIONS
# ─────────────────────────────────────────────

CATEGORIES = ["Food", "Transport", "Shopping", "Utilities",
              "Health", "Entertainment", "Education", "Other"]


def add_expense():
    """
    Ask for a date ONCE, then how many expenses to add,
    then collect each expense in a loop without re-asking the date.
    After all are saved, show the daily inventory for that date.
    """
    print("\n-- Add Expense --")

    # Step 1: ask date only once
    date_input = input("  Date (YYYY-MM-DD) [press Enter for today]: ").strip()
    if not date_input:
        date = datetime.date.today().isoformat()
    else:
        try:
            datetime.datetime.strptime(date_input, "%Y-%m-%d")
            date = date_input
        except ValueError:
            print("  Invalid date format. Please use YYYY-MM-DD.")
            return

    # Step 2: ask how many expenses to add
    try:
        count = int(input("  How many expenses to add? ").strip())
        if count <= 0:
            raise ValueError
    except ValueError:
        print("  Please enter a valid positive number.")
        return

    cat_legend = "  " + "  ".join(f"{i+1}.{c}" for i, c in enumerate(CATEGORIES))
    saved_count = 0

    # Step 3: loop through all expenses without interruption
    for i in range(1, count + 1):
        print(f"\n  --- Expense {i} of {count} ---")

        # Amount
        try:
            amount = float(input("  Amount (Rs): ").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            print("  Invalid amount - skipping this entry.")
            continue

        # Category
        print(cat_legend)
        cat_input = input("  Category (number or name): ").strip()
        if cat_input.isdigit() and 1 <= int(cat_input) <= len(CATEGORIES):
            category = CATEGORIES[int(cat_input) - 1]
        elif cat_input:
            category = cat_input.title()
        else:
            category = "Other"

        # Description
        description = input("  Description (optional): ").strip()

        save_expense(date, amount, category, description)
        saved_count += 1
        print(f"  Saved Rs {amount:.2f} - {category}")

    # Step 4: auto-show daily inventory once all are saved
    if saved_count:
        print(f"\n  {saved_count} expense(s) added for {date}.")
        view_daily_inventory(date)


def view_all_expenses():
    """
    Show ALL expenses from the very beginning, grouped by date,
    with a per-date subtotal and a grand total at the end.
    """
    print("\n-- All Expenses (from the start) --")
    dates = load_all_dates()
    if not dates:
        print("  No expenses recorded yet.")
        return

    grand_total = 0.0
    grand_count = 0

    for date in dates:
        rows = load_expenses_for_date(date)
        day_total = sum(r["amount"] for r in rows)
        grand_total += day_total
        grand_count += len(rows)

        print(f"\n  +-- {date}  ({len(rows)} expense(s))  Day total: Rs {day_total:.2f}")
        print(f"  |  {'ID':>4}  {'Amount (Rs)':>12}  {'Category':<16} Description")
        print(f"  |  {'-'*56}")
        for r in rows:
            desc = (r["description"] or "")[:30]
            print(f"  |  {r['id']:>4}  {r['amount']:>12.2f}  {r['category']:<16} {desc}")
        print(f"  +{'-'*60}")

    print(f"\n  Grand total: Rs {grand_total:.2f}  across {grand_count} transaction(s) "
          f"on {len(dates)} day(s)\n")


def view_daily_inventory(date_str=None):
    """
    Show a full inventory of all expenses for a specific date,
    with a category breakdown and day total.
    If date_str is not provided, ask the user.
    """
    if date_str is None:
        print("\n-- Daily Inventory --")
        date_input = input("  Enter date (YYYY-MM-DD) [press Enter for today]: ").strip()
        if not date_input:
            date_str = datetime.date.today().isoformat()
        else:
            try:
                datetime.datetime.strptime(date_input, "%Y-%m-%d")
                date_str = date_input
            except ValueError:
                print("  Invalid date format.")
                return

    rows = load_expenses_for_date(date_str)
    if not rows:
        print(f"  No expenses recorded for {date_str}.")
        return

    day_total = sum(r["amount"] for r in rows)

    print(f"\n  === Inventory for {date_str}  ({len(rows)} expense(s)) ===")
    print(f"  {'ID':>4}  {'Amount (Rs)':>12}  {'Category':<16} Description")
    print(f"  {'='*58}")
    for r in rows:
        desc = (r["description"] or "")[:30]
        print(f"  {r['id']:>4}  {r['amount']:>12.2f}  {r['category']:<16} {desc}")

    # Category breakdown
    cat_totals = {}
    for r in rows:
        cat_totals[r["category"]] = cat_totals.get(r["category"], 0.0) + r["amount"]

    print(f"\n  --- Category Breakdown ---")
    for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        pct = amt / day_total * 100
        bar = "#" * int(pct / 5)
        print(f"  {cat:<16} Rs {amt:>8.2f}  {pct:>5.1f}%  {bar}")

    print(f"  {'='*58}")
    print(f"  {'DAY TOTAL':<16} Rs {day_total:>8.2f}  100.0%\n")


def filter_by_date_range(start_date=None, end_date=None):
    """Return expenses between start_date and end_date (inclusive)."""
    if start_date is None or end_date is None:
        print("\n-- Filter by Date Range --")
        print("  Presets: 1. Today  2. Last 7 days  3. This month  4. Custom")
        choice = input("  Choose: ").strip()

        today = datetime.date.today()
        if choice == "1":
            start_date = end_date = today
        elif choice == "2":
            start_date = today - datetime.timedelta(days=6)
            end_date = today
        elif choice == "3":
            start_date = today.replace(day=1)
            end_date = today
        else:
            try:
                start_date = datetime.date.fromisoformat(
                    input("  Start date (YYYY-MM-DD): ").strip()
                )
                end_date = datetime.date.fromisoformat(
                    input("  End date   (YYYY-MM-DD): ").strip()
                )
            except ValueError:
                print("  Invalid date format.")
                return []

    s = str(start_date)
    e = str(end_date)

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE date >= ? AND date <= ? ORDER BY date DESC, id DESC",
        (s, e)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    _print_table(rows, title=f"Expenses from {s} to {e}")
    return rows


def generate_total_report():
    """Show total spending for a user-chosen period."""
    print("\n-- Total Spending Report --")
    rows = filter_by_date_range()
    if rows:
        total = sum(r["amount"] for r in rows)
        print(f"\n  Total spending: Rs {total:.2f}  ({len(rows)} transaction(s))")


def generate_category_report():
    """Show spending grouped by category for a user-chosen period."""
    print("\n-- Category-wise Report --")
    rows = filter_by_date_range()
    if not rows:
        return

    totals = {}
    for r in rows:
        totals[r["category"]] = totals.get(r["category"], 0.0) + r["amount"]

    grand_total = sum(totals.values())

    print(f"\n  {'Category':<20} {'Amount (Rs)':>12}  {'Share':>7}")
    print("  " + "-" * 44)
    for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / grand_total * 100) if grand_total else 0
        print(f"  {cat:<20} {amt:>12.2f}  {pct:>6.1f}%")
    print("  " + "-" * 44)
    print(f"  {'TOTAL':<20} {grand_total:>12.2f}  {'100.0%':>7}")


def delete_expense():
    """Show all expenses, then delete one by ID after confirmation."""
    print("\n-- Delete Expense --")
    expenses = load_expenses()
    if not expenses:
        print("  No expenses to delete.")
        return

    _print_table(expenses)

    id_input = input("  Enter the ID to delete (or press Enter to cancel): ").strip()
    if not id_input:
        print("  Cancelled.")
        return

    if not id_input.isdigit():
        print("  Invalid ID.")
        return

    expense_id = int(id_input)
    match = next((r for r in expenses if r["id"] == expense_id), None)
    if not match:
        print(f"  No expense found with ID {expense_id}.")
        return

    print(f"  About to delete: [{match['date']}] Rs {match['amount']:.2f} - "
          f"{match['category']}  {match['description'] or ''}")
    confirm = input("  Are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    print(f"  Expense ID {expense_id} deleted.")


# ─────────────────────────────────────────────
# DISPLAY HELPER
# ─────────────────────────────────────────────

def _print_table(rows, title="All Expenses"):
    """Pretty-print a flat list of expense dicts."""
    if not rows:
        print(f"\n  No expenses found.")
        return

    print(f"\n  -- {title} ({len(rows)} record(s)) --")
    print(f"  {'ID':>4}  {'Date':<12} {'Amount (Rs)':>12}  {'Category':<16} Description")
    print("  " + "-" * 68)
    for r in rows:
        desc = (r["description"] or "")[:30]
        print(f"  {r['id']:>4}  {r['date']:<12} {r['amount']:>12.2f}  {r['category']:<16} {desc}")
    print()


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

MENU = """
+====================================+
|    Personal Expense Tracker        |
+====================================+
|  1. Add expenses                   |
|  2. View all expenses              |
|  3. View daily inventory           |
|  4. Filter by date range           |
|  5. Show total spending            |
|  6. Show category-wise report      |
|  7. Delete an expense              |
|  8. Exit                           |
+====================================+
"""


def main():
    init_db()
    print("  Expense Tracker started. Data stored in:", os.path.abspath(DB_FILE))

    actions = {
        "1": add_expense,
        "2": view_all_expenses,
        "3": view_daily_inventory,
        "4": filter_by_date_range,
        "5": generate_total_report,
        "6": generate_category_report,
        "7": delete_expense,
    }

    while True:
        print(MENU)
        choice = input("  Enter choice (1-8): ").strip()

        if choice == "8":
            print("  Goodbye! Your data is saved.\n")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("  Invalid option. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main()
