import json
import os
import sys
from datetime import datetime


# ── Optional pandas import ──────────────────────────────────────────────────
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# ── Constants ────────────────────────────────────────────────────────────────
# ── Data file ────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inventory.json")
SEPARATOR = "─" * 60


# ════════════════════════════════════════════════════════════════
# 1. DATA PERSISTENCE  (load / save)
# ════════════════════════════════════════════════════════════════

def load_data() -> list[dict]:
    """Load inventory records from the JSON file.

    Returns an empty list if the file does not exist or is corrupt.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array at the top level.")
        return data
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"[WARNING] Could not read '{DATA_FILE}': {exc}")
        print("          Starting with an empty inventory.\n")
        return []


def save_data(inventory: list[dict]) -> None:
    """Persist inventory records to the JSON file (pretty-printed)."""
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(inventory, fh, indent=4, ensure_ascii=False)


# ════════════════════════════════════════════════════════════════
# 2. ID HELPERS
# ════════════════════════════════════════════════════════════════

def _next_id(inventory: list[dict]) -> int:
    """Return the next available integer ID (auto-increment style)."""
    if not inventory:
        return 1
    return max(item["id"] for item in inventory) + 1


def _find_by_id(inventory: list[dict], product_id: int) -> dict | None:
    """Return the first item whose id matches, or None."""
    for item in inventory:
        if item["id"] == product_id:
            return item
    return None


# ════════════════════════════════════════════════════════════════
# 3. INPUT HELPERS  (validation)
# ════════════════════════════════════════════════════════════════

def _input_str(prompt: str, allow_empty: bool = False) -> str:
    """Prompt for a non-empty string (unless allow_empty=True)."""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("    This field cannot be empty. Please try again.")


def _input_int(prompt: str, min_val: int = 0) -> int:
    """Prompt for an integer ≥ min_val."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value >= min_val:
                return value
            print(f"    Value must be ≥ {min_val}.")
        except ValueError:
            print("    Please enter a whole number.")


def _input_float(prompt: str, min_val: float = 0.0) -> float:
    """Prompt for a float ≥ min_val."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value >= min_val:
                return value
            print(f"    Value must be ≥ {min_val}.")
        except ValueError:
            print("   Please enter a valid number (e.g. 9.99).")


# ════════════════════════════════════════════════════════════════
# 4. DISPLAY HELPERS
# ════════════════════════════════════════════════════════════════

def _print_item(item: dict) -> None:
    """Pretty-print a single inventory record."""
    print(f"""
  ┌─ ID #{item['id']} ──────────────────────────────
  │  Name      : {item['name']}
  │  Category  : {item['category']}
  │  Quantity  : {item['quantity']}
  │  Price     : ₹{item['price']:.2f}
  │  Added On  : {item.get('added_on', 'N/A')}
  └────────────────────────────────────────────""")


def _print_table(inventory: list[dict]) -> None:
    """Print all items in a compact table."""
    if not inventory:
        print("\n  (No records to display)\n")
        return
    header = f"{'S.No':>5}  {'ID':>4}  {'Name':<22}  {'Category':<14}  {'Qty':>6}  {'Price':>10}"
    print(f"\n  {header}")
    print(f"  {'─'*5}  {'─'*4}  {'─'*22}  {'─'*14}  {'─'*6}  {'─'*10}")
    for sno, item in enumerate(inventory, start=1):
     print(
         f"  {sno:>5}  "
        f"{item['id']:>4}  "
        f"{item['name']:<22}  "
        f"{item['category']:<14}  "
        f"{item['quantity']:>6}  "
        f"₹{item['price']:>9.2f}"
    )
    print()


# ════════════════════════════════════════════════════════════════
# 5. CRUD OPERATIONS
# ════════════════════════════════════════════════════════════════

# ── 5a. CREATE ───────────────────────────────────────────────────

def add_item(inventory: list[dict]) -> None:
    """Collect product details from the user and append a new record."""
    print(f"\n  {'─'*40}")
    print("    ADD NEW PRODUCT")
    print(f"  {'─'*40}")

    name     = _input_str("  Product name     : ")
    category = _input_str("  Category         : ")
    quantity = _input_int("  Initial quantity : ", min_val=0)
    price    = _input_float("  Unit price (₹)   : ", min_val=0.0)

    new_item = {
        "id"      : _next_id(inventory),
        "name"    : name,
        "category": category,
        "quantity": quantity,
        "price"   : round(price, 2),
        "added_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    inventory.append(new_item)
    save_data(inventory)

    print(f"\n    '{name}' added successfully with ID #{new_item['id']}.")


# ── 5b. READ ────────────────────────────────────────────────────

def view_all(inventory: list[dict]) -> None:
    """Display every product in a compact table."""
    print(f"\n  {'─'*40}")
    print(f"    ALL PRODUCTS  ({len(inventory)} records)")
    print(f"  {'─'*40}")
    _print_table(inventory)


# ── 5c. UPDATE ──────────────────────────────────────────────────

def update_item(inventory: list[dict]) -> None:
    """Update one or more fields of an existing product by ID."""
    print(f"\n  {'─'*40}")
    print("     UPDATE PRODUCT")
    print(f"  {'─'*40}")

    product_id = _input_int("  Enter product ID to update: ", min_val=1)
    item = _find_by_id(inventory, product_id)

    if item is None:
        print(f"\n    No product found with ID #{product_id}.")
        return

    _print_item(item)
    print("  (Leave a field blank to keep its current value)\n")

    name = _input_str(f"  New name [{item['name']}]         : ", allow_empty=True)
    cat  = _input_str(f"  New category [{item['category']}]  : ", allow_empty=True)

    # Quantity
    raw_qty = input(f"  New quantity [{item['quantity']}]       : ").strip()
    if raw_qty:
        try:
            qty = int(raw_qty)
            if qty < 0:
                raise ValueError
            item["quantity"] = qty
        except ValueError:
            print("    Invalid quantity — keeping original.")

    # Price
    raw_price = input(f"  New price [₹{item['price']:.2f}]          : ").strip()
    if raw_price:
        try:
            price = float(raw_price)
            if price < 0:
                raise ValueError
            item["price"] = round(price, 2)
        except ValueError:
            print("  ⚠  Invalid price — keeping original.")

    if name:
        item["name"] = name
    if cat:
        item["category"] = cat

    item["updated_on"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_data(inventory)
    print(f"\n    Product #{product_id} updated successfully.")


# ── 5d. DELETE ──────────────────────────────────────────────────

def delete_item(inventory: list[dict]) -> None:
    """Remove a product from the inventory after confirmation."""
    print(f"\n  {'─'*40}")
    print("     DELETE PRODUCT")
    print(f"  {'─'*40}")

    product_id = _input_int("  Enter product ID to delete: ", min_val=1)
    item = _find_by_id(inventory, product_id)

    if item is None:
        print(f"\n    No product found with ID #{product_id}.")
        return

    _print_item(item)
    confirm = input("  Are you sure you want to delete this product? (yes/no): ").strip().lower()
    if confirm in ("yes", "y"):
        inventory.remove(item)
        save_data(inventory)
        print(f"\n    Product #{product_id} deleted successfully.")
    else:
        print("\n    Deletion cancelled.")


# ════════════════════════════════════════════════════════════════
# 6. SEARCH
# ════════════════════════════════════════════════════════════════

def search_items(inventory: list[dict]) -> None:
    """Search by ID, name substring, or category."""
    print(f"\n  {'─'*40}")
    print("    SEARCH PRODUCTS")
    print(f"  {'─'*40}")
    print("  [1] Search by ID")
    print("  [2] Search by Name")
    print("  [3] Search by Category")
    choice = input("\n  Select search type (1/2/3): ").strip()

    results: list[dict] = []

    if choice == "1":
        product_id = _input_int("  Enter product ID: ", min_val=1)
        item = _find_by_id(inventory, product_id)
        if item:
            results = [item]

    elif choice == "2":
        keyword = _input_str("  Enter name keyword: ").lower()
        results = [i for i in inventory if keyword in i["name"].lower()]

    elif choice == "3":
        keyword = _input_str("  Enter category keyword: ").lower()
        results = [i for i in inventory if keyword in i["category"].lower()]

    else:
        print("    Invalid option.")
        return

    if results:
        print(f"\n  Found {len(results)} result(s):\n")
        for item in results:
            _print_item(item)
    else:
        print("\n  No products match your search.\n")


# ════════════════════════════════════════════════════════════════
# 7. REPORTS  (pandas)
# ════════════════════════════════════════════════════════════════

def generate_report(inventory: list[dict]) -> None:
    """Generate analytics using pandas (if available)."""
    print(f"\n  {'─'*40}")
    print("   INVENTORY REPORT")
    print(f"  {'─'*40}")

    if not inventory:
        print("\n  (Inventory is empty — nothing to report)\n")
        return

    if not PANDAS_AVAILABLE:
        # Fallback: manual calculations
        total_value = sum(i["quantity"] * i["price"] for i in inventory)
        total_items = sum(i["quantity"] for i in inventory)
        categories  = {}
        for item in inventory:
            cat = item["category"]
            categories.setdefault(cat, {"count": 0, "value": 0.0})
            categories[cat]["count"]  += item["quantity"]
            categories[cat]["value"]  += item["quantity"] * item["price"]

        print(f"\n  Total distinct products : {len(inventory)}")
        print(f"  Total units in stock    : {total_items}")
        print(f"  Total inventory value   : ₹{total_value:,.2f}")
        print("\n  By Category:")
        for cat, stats in categories.items():
            print(f"    • {cat:<16} → {stats['count']:>5} units  |  ₹{stats['value']:>10,.2f}")
        print()
        return

    # ── pandas path ──────────────────────────────────────────────
    df = pd.DataFrame(inventory)
    df["total_value"] = df["quantity"] * df["price"]

    print(f"\n  Total distinct products : {len(df)}")
    print(f"  Total units in stock    : {df['quantity'].sum()}")
    print(f"  Total inventory value   : ₹{df['total_value'].sum():,.2f}")
    print(f"  Average unit price      : ₹{df['price'].mean():.2f}")
    print(f"  Most expensive item     : {df.loc[df['price'].idxmax(), 'name']}  "
          f"(₹{df['price'].max():.2f})")
    print(f"  Lowest stock item       : {df.loc[df['quantity'].idxmin(), 'name']}  "
          f"(qty: {df['quantity'].min()})")

    print("\n  ── Summary by Category ──────────────────────────────")
    summary = (
        df.groupby("category")
          .agg(
              Products=("id", "count"),
              Total_Units=("quantity", "sum"),
              Avg_Price=("price", "mean"),
              Total_Value=("total_value", "sum"),
          )
          .sort_values("Total_Value", ascending=False)
    )
    # Pretty-print the summary table
    print()
    col_h = f"  {'Category':<16}  {'Products':>8}  {'Units':>7}  {'Avg Price':>10}  {'Total Value':>12}"
    print(col_h)
    print(f"  {'─'*16}  {'─'*8}  {'─'*7}  {'─'*10}  {'─'*12}")
    for cat, row in summary.iterrows():
        print(
            f"  {cat:<16}  {int(row['Products']):>8}  {int(row['Total_Units']):>7}  "
            f"₹{row['Avg_Price']:>9.2f}  ₹{row['Total_Value']:>11,.2f}"
        )
    print()

    # Low-stock alert (qty < 5)
    low_stock = df[df["quantity"] < 5]
    if not low_stock.empty:
        print("     LOW STOCK ALERT (quantity < 5):")
        for _, row in low_stock.iterrows():
            print(f"       • [{row['id']}] {row['name']}  —  {row['quantity']} unit(s) left")
        print()


# ════════════════════════════════════════════════════════════════
# 8. SEED DATA  (demo convenience)
# ════════════════════════════════════════════════════════════════

def seed_demo_data(inventory: list[dict]) -> None:
    """Populate the inventory with sample records for demo purposes."""
    if inventory:
        print("\n     Inventory already has data — skipping seed.\n")
        return
    demo_items = [
        ("Wireless Mouse",        "Electronics",   45,  599.00),
        ("Mechanical Keyboard",   "Electronics",    8, 2499.00),
        ("USB-C Hub 7-in-1",      "Electronics",   22,  899.00),
        ("A4 Paper Ream 500",     "Stationery",   120,  245.00),
        ("Blue Ballpoint Pens x10","Stationery",   80,   85.00),
        ("Sticky Notes Pack",     "Stationery",    60,   49.00),
        ("Office Chair",          "Furniture",      4, 6999.00),
        ("Standing Desk",         "Furniture",      2,15999.00),
        ("Whiteboard 4x3 ft",     "Furniture",      7, 2200.00),
        ("Hand Sanitizer 500ml",  "Hygiene",       90,   99.00),
    ]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for name, category, qty, price in demo_items:
        inventory.append({
            "id"      : _next_id(inventory),
            "name"    : name,
            "category": category,
            "quantity": qty,
            "price"   : price,
            "added_on": ts,
        })
    save_data(inventory)
    print(f"\n    {len(demo_items)} demo products loaded.\n")

def clear_all_data(inventory: list[dict]) -> None:
   
    if not inventory:
        print("\n    Inventory is already empty.\n")
        return
    print(f"\n     This will permanently delete ALL {len(inventory)} products!")
    confirm = input("  Type YES to confirm: ").strip()
    if confirm == "YES":
        inventory.clear()
        save_data(inventory)
        print("\n    All data cleared. You can now add your own products.\n")
    else:
        print("\n     Cancelled — no data was deleted.\n")


# ════════════════════════════════════════════════════════════════
# 9. MAIN MENU
# ════════════════════════════════════════════════════════════════

MENU = """
╔══════════════════════════════════════════╗
║     MINI INVENTORY MANAGER  v1.0         ║
╠══════════════════════════════════════════╣
║  1 · View all products                   ║
║  2 · Add a new product                   ║
║  3 · Update a product                    ║
║  4 · Delete a product                    ║
║  5 · Search products                     ║
║  6 · Generate report                     ║
║  7 · Load demo data                      ║
║  8 · Clear all data                      ║
║  0 · Exit                                ║
╚══════════════════════════════════════════╝
"""

ACTION_MAP = {
    "1": view_all,
    "2": add_item,
    "3": update_item,
    "4": delete_item,
    "5": search_items,
    "6": generate_report,
    "8": clear_all_data, 
}


def main() -> None:
    """Entry point – menu-driven loop."""
    inventory = load_data()

    print("\n  Welcome to Mini Inventory Management System!")
    if PANDAS_AVAILABLE:
        print("   pandas detected — full reports enabled.")
    else:
        print("    pandas not found — basic reports only.")
        print("       Install with:  pip install pandas")

    while True:
        print(MENU)
        choice = input("  Select an option: ").strip()

        if choice == "0":
            print("\n    Goodbye! Data saved to", DATA_FILE, "\n")
            sys.exit(0)

        elif choice == "7":
            seed_demo_data(inventory)

        elif choice in ACTION_MAP:
            ACTION_MAP[choice](inventory)

        else:
            print("\n  ⚠  Invalid choice — please enter 0–8.\n")

        input("\n  Press ENTER to return to the menu...")


# ── Entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    main()