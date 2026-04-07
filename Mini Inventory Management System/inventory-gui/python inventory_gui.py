"""
╔══════════════════════════════════════════════════════╗
║   Mini Inventory Management System — GUI Version     ║
║   Built with tkinter (no extra install needed)       ║
║   Same logic as inventory_manager.py (CLI version)   ║
╚══════════════════════════════════════════════════════╝
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# ── Optional pandas ──────────────────────────────────────────────
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# ── Data file ────────────────────────────────────────────────────
# ── Data file ────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inventory.json")


# ════════════════════════════════════════════════════════════════
# 1. DATA PERSISTENCE  (same as CLI version)
# ════════════════════════════════════════════════════════════════

def load_data() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def save_data(inventory: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(inventory, fh, indent=4, ensure_ascii=False)


def _next_id(inventory: list) -> int:
    return max((item["id"] for item in inventory), default=0) + 1


# ════════════════════════════════════════════════════════════════
# 2. DIALOG WINDOWS  (Add / Edit)
# ════════════════════════════════════════════════════════════════

class ProductDialog(tk.Toplevel):
    """
    Popup dialog for adding or editing a product.
    Works for both Add (item=None) and Edit (item=dict).
    """
    def __init__(self, parent, item=None):
        super().__init__(parent)
        self.result = None
        self.item   = item

        title = "Edit Product" if item else "Add New Product"
        self.title(title)
        self.resizable(False, False)
        self.grab_set()                      # modal — blocks main window
        self.configure(padx=20, pady=20)

        # ── Labels & Entry fields ──
        fields = [("Product Name", "name"),
                  ("Category",     "category"),
                  ("Quantity",     "quantity"),
                  ("Price (Rs.)",  "price")]

        self.entries = {}
        for row, (label, key) in enumerate(fields):
            tk.Label(self, text=label, anchor="w", width=14).grid(
                row=row, column=0, sticky="w", pady=4)
            entry = tk.Entry(self, width=28)
            entry.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))
            # Pre-fill when editing
            if item and key in item:
                entry.insert(0, str(item[key]))
            self.entries[key] = entry

        # ── Buttons ──
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2,
                       pady=(16, 0), sticky="e")
        tk.Button(btn_frame, text="Cancel", width=8,
                  command=self.destroy).pack(side="right", padx=(6, 0))
        tk.Button(btn_frame, text="Save", width=8,
                  command=self._save).pack(side="right")

        # Focus first empty field
        self.entries["name"].focus_set()
        self.wait_window()                   # block until dialog closes

    def _save(self):
        name     = self.entries["name"].get().strip()
        category = self.entries["category"].get().strip()
        qty_raw  = self.entries["quantity"].get().strip()
        price_raw= self.entries["price"].get().strip()

        # ── Validation ──
        if not name:
            messagebox.showerror("Error", "Product name cannot be empty.", parent=self)
            return
        if not category:
            messagebox.showerror("Error", "Category cannot be empty.", parent=self)
            return
        try:
            qty = int(qty_raw)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a whole number >= 0.", parent=self)
            return
        try:
            price = float(price_raw)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Price must be a number >= 0.", parent=self)
            return

        self.result = {
            "name"    : name,
            "category": category,
            "quantity": qty,
            "price"   : round(price, 2),
        }
        self.destroy()


# ════════════════════════════════════════════════════════════════
# 3. REPORT WINDOW
# ════════════════════════════════════════════════════════════════

class ReportWindow(tk.Toplevel):
    """Popup window showing inventory analytics."""
    def __init__(self, parent, inventory: list):
        super().__init__(parent)
        self.title("Inventory Report")
        self.geometry("600x480")
        self.configure(padx=16, pady=16)

        tk.Label(self, text="Inventory Report",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))

        # Scrollable text area
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        text = tk.Text(frame, font=("Courier New", 10),
                       yscrollcommand=scrollbar.set, wrap="none",
                       relief="flat", padx=8, pady=8)
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        content = self._build_report(inventory)
        text.insert("end", content)
        text.config(state="disabled")

    def _build_report(self, inventory: list) -> str:
        if not inventory:
            return "  Inventory is empty — nothing to report."

        lines = []
        sep = "─" * 52

        if PANDAS_AVAILABLE:
            df = pd.DataFrame(inventory)
            df["total_value"] = df["quantity"] * df["price"]
            lines += [
                sep,
                f"  Total distinct products : {len(df)}",
                f"  Total units in stock    : {df['quantity'].sum()}",
                f"  Total inventory value   : Rs.{df['total_value'].sum():,.2f}",
                f"  Average unit price      : Rs.{df['price'].mean():.2f}",
                f"  Most expensive item     : {df.loc[df['price'].idxmax(), 'name']}",
                f"  Lowest stock item       : {df.loc[df['quantity'].idxmin(), 'name']}",
                sep,
                "",
                f"  {'Category':<16}  {'Prods':>5}  {'Units':>6}  {'Avg Price':>10}  {'Total Value':>12}",
                f"  {'─'*16}  {'─'*5}  {'─'*6}  {'─'*10}  {'─'*12}",
            ]
            summary = (df.groupby("category")
                         .agg(P=("id","count"), U=("quantity","sum"),
                              A=("price","mean"), V=("total_value","sum"))
                         .sort_values("V", ascending=False))
            for cat, row in summary.iterrows():
                lines.append(
                    f"  {cat:<16}  {int(row['P']):>5}  {int(row['U']):>6}"
                    f"  Rs.{row['A']:>9.2f}  Rs.{row['V']:>11,.2f}"
                )

            low = df[df["quantity"] < 5]
            if not low.empty:
                lines += ["", sep, "  LOW STOCK ALERT (qty < 5):", sep]
                for _, r in low.iterrows():
                    lines.append(f"  [{int(r['id'])}] {r['name']}  —  {int(r['quantity'])} unit(s) left")
        else:
            # Manual fallback
            total_value = sum(i["quantity"] * i["price"] for i in inventory)
            total_units = sum(i["quantity"] for i in inventory)
            cat_map = {}
            for i in inventory:
                c = i["category"]
                cat_map.setdefault(c, {"count": 0, "value": 0.0})
                cat_map[c]["count"] += i["quantity"]
                cat_map[c]["value"] += i["quantity"] * i["price"]

            lines += [
                sep,
                f"  Total distinct products : {len(inventory)}",
                f"  Total units in stock    : {total_units}",
                f"  Total inventory value   : Rs.{total_value:,.2f}",
                sep,
                "",
                "  By Category:",
            ]
            for cat, s in cat_map.items():
                lines.append(f"    {cat:<18} {s['count']:>5} units  |  Rs.{s['value']:>10,.2f}")

            low = [i for i in inventory if i["quantity"] < 5]
            if low:
                lines += ["", sep, "  LOW STOCK ALERT (qty < 5):", sep]
                for i in low:
                    lines.append(f"  [{i['id']}] {i['name']}  —  {i['quantity']} unit(s) left")

        return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# 4. MAIN APPLICATION WINDOW
# ════════════════════════════════════════════════════════════════

class InventoryApp(tk.Tk):
    """Main tkinter application window."""

    COLUMNS    = ("S.No", "ID", "Name", "Category", "Quantity", "Price (Rs.)", "Status", "Added On")
    COL_WIDTHS = (45, 45, 190, 120, 70, 100, 60, 130)

    def __init__(self):
        super().__init__()
        self.title("Mini Inventory Management System")
        self.geometry("900x580")
        self.minsize(750, 480)

        self.inventory = load_data()

        self._build_ui()
        self._refresh_table()
        self._update_stats()

    # ── UI CONSTRUCTION ─────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, pady=10, padx=12)
        top.pack(fill="x")
        tk.Label(top, text="Inventory Manager",
                 font=("Segoe UI", 15, "bold")).pack(side="left")

        btn_frame = tk.Frame(top)
        btn_frame.pack(side="right")
        for text, cmd, bg in [
            ("Load Demo Data", self.load_demo,   "#e8f4fd"),
            ("Clear All Data", self.clear_all,   "#fdecea"),
            ("Report",         self.show_report, "#f0fdf4"),
            ("Add Product",    self.add_item,    "#e8f4fd"),
        ]:
            tk.Button(btn_frame, text=text, command=cmd, bg=bg,
                      relief="groove", padx=10, pady=4).pack(side="left", padx=4)

        # Stats bar
        self.stats_frame = tk.Frame(self, bg="#f5f5f5", pady=8, padx=12)
        self.stats_frame.pack(fill="x")
        self.stat_labels = {}
        for key in ("Products", "Total Units", "Inventory Value", "Low Stock"):
            box = tk.Frame(self.stats_frame, bg="#f5f5f5", padx=14)
            box.pack(side="left")
            tk.Label(box, text=key, bg="#f5f5f5",
                     font=("Segoe UI", 9), fg="#666").pack(anchor="w")
            lbl = tk.Label(box, text="—", bg="#f5f5f5",
                           font=("Segoe UI", 13, "bold"))
            lbl.pack(anchor="w")
            self.stat_labels[key] = lbl

        # Search / filter bar
        bar = tk.Frame(self, padx=12, pady=6)
        bar.pack(fill="x")

        tk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_table())
        tk.Entry(bar, textvariable=self.search_var, width=28).pack(
            side="left", padx=(4, 16))

        tk.Label(bar, text="Category:").pack(side="left")
        self.cat_var = tk.StringVar(value="All")
        self.cat_menu = ttk.Combobox(bar, textvariable=self.cat_var,
                                     state="readonly", width=16)
        self.cat_menu.pack(side="left", padx=4)
        self.cat_menu.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        # Table
        tbl_frame = tk.Frame(self, padx=12)
        tbl_frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical")
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal")
        self.tree = ttk.Treeview(
            tbl_frame,
            columns=self.COLUMNS,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        for col, width in zip(self.COLUMNS, self.COL_WIDTHS):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=width, minwidth=40,
                             anchor="e" if col in ("Quantity", "Price (Rs.)") else "w")

        # Row colour tags
        self.tree.tag_configure("low",  background="#fff3f3")
        self.tree.tag_configure("even", background="#fafafa")

        # Double-click → edit
        self.tree.bind("<Double-1>", lambda _: self.edit_item())

        # Bottom action bar
        bot = tk.Frame(self, padx=12, pady=8)
        bot.pack(fill="x")
        for text, cmd in [("Edit Selected", self.edit_item),
                          ("Delete Selected", self.delete_item)]:
            tk.Button(bot, text=text, command=cmd,
                      relief="groove", padx=10, pady=3).pack(side="left", padx=4)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, anchor="w",
                 fg="#555", font=("Segoe UI", 9)).pack(
            fill="x", padx=12, pady=(0, 6))

    # ── TABLE HELPERS ────────────────────────────────────────────

    def _filtered(self) -> list:
        q   = self.search_var.get().lower()
        cat = self.cat_var.get()
        return [
            i for i in self.inventory
            if (not q or q in i["name"].lower() or q in i["category"].lower())
            and (cat == "All" or i["category"] == cat)
        ]

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        rows = self._filtered()
        for idx, item in enumerate(rows):
            status = "Low" if item["quantity"] < 5 else "OK"
            tag    = "low" if item["quantity"] < 5 else ("even" if idx % 2 == 0 else "")
            self.tree.insert("", "end", iid=str(item["id"]),
                 values=(
                     idx + 1,
                     item["id"],
                     item["name"],
                     item["category"],
                     item["quantity"],
                     f"Rs.{item['price']:.2f}",
                     status,
                     item.get("added_on", "—"),
                 ), tags=(tag,))
        self._update_cat_menu()
        self._update_stats()
        self.status_var.set(f"Showing {len(rows)} of {len(self.inventory)} products")

    def _update_cat_menu(self):
        cats = ["All"] + sorted({i["category"] for i in self.inventory})
        self.cat_menu["values"] = cats
        if self.cat_var.get() not in cats:
            self.cat_var.set("All")

    def _update_stats(self):
        total_val  = sum(i["quantity"] * i["price"] for i in self.inventory)
        total_units= sum(i["quantity"] for i in self.inventory)
        low_count  = sum(1 for i in self.inventory if i["quantity"] < 5)

        self.stat_labels["Products"].config(text=str(len(self.inventory)))
        self.stat_labels["Total Units"].config(text=str(total_units))
        self.stat_labels["Inventory Value"].config(text=f"Rs.{total_val:,.2f}")
        self.stat_labels["Low Stock"].config(
            text=str(low_count),
            fg="red" if low_count > 0 else "black"
        )

    def _sort_by(self, col):
        """Sort table rows by clicking a column header."""
        key_map = {
             "S.No": None,
             "ID": "id", "Name": "name", "Category": "category",
             "Quantity": "quantity", "Price (Rs.)": "price",
              }
        key = key_map.get(col)
        if not key:
            return
        self.inventory.sort(key=lambda x: x[key])
        self._refresh_table()

    def _selected_item(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a product first.")
            return None
        pid = int(sel[0])
        return next((i for i in self.inventory if i["id"] == pid), None)

    # ── CRUD ACTIONS ─────────────────────────────────────────────

    def add_item(self):
        dlg = ProductDialog(self)
        if dlg.result:
            new_item = {
                "id"      : _next_id(self.inventory),
                "added_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                **dlg.result,
            }
            self.inventory.append(new_item)
            save_data(self.inventory)
            self._refresh_table()
            self.status_var.set(f"Added '{new_item['name']}' (ID #{new_item['id']})")

    def edit_item(self):
        item = self._selected_item()
        if not item:
            return
        dlg = ProductDialog(self, item=item)
        if dlg.result:
            item.update(dlg.result)
            item["updated_on"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_data(self.inventory)
            self._refresh_table()
            self.status_var.set(f"Updated '{item['name']}' (ID #{item['id']})")

    def delete_item(self):
        item = self._selected_item()
        if not item:
            return
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{item['name']}' (ID #{item['id']})?\nThis cannot be undone."
        )
        if confirmed:
            self.inventory.remove(item)
            save_data(self.inventory)
            self._refresh_table()
            self.status_var.set(f"Deleted '{item['name']}'")

    # ── OTHER ACTIONS ────────────────────────────────────────────

    def clear_all(self):
        if not self.inventory:
            messagebox.showinfo("Empty", "Inventory is already empty.")
            return

        # First confirmation
        confirmed = messagebox.askyesno(
            "Clear All Data",
            f"This will permanently delete ALL {len(self.inventory)} products.\n\nAre you sure?"
        )
        if not confirmed:
            self.status_var.set("Clear cancelled.")
            return

        # Second confirmation — type YES
        answer = simpledialog.askstring(
            "Final Confirmation",
            "Type YES to permanently delete all products:",
            parent=self
        )
        if answer and answer.upper() == "YES":
            self.inventory.clear()
            save_data(self.inventory)
            self._refresh_table()
            self.status_var.set("All data cleared. You can now add your own products.")
        else:
            self.status_var.set("Clear cancelled — no data was deleted.")

    def load_demo(self):
        if self.inventory:
            messagebox.showinfo(
                "Demo Data",
                "Inventory already has data.\nClear all data first, then load demo."
            )
            return
        demo_items = [
            ("Wireless Mouse",          "Electronics", 45,  599.00),
            ("Mechanical Keyboard",     "Electronics",  8, 2499.00),
            ("USB-C Hub 7-in-1",        "Electronics", 22,  899.00),
            ("A4 Paper Ream 500",       "Stationery", 120,  245.00),
            ("Blue Ballpoint Pens x10", "Stationery",  80,   85.00),
            ("Sticky Notes Pack",       "Stationery",  60,   49.00),
            ("Office Chair",            "Furniture",    4, 6999.00),
            ("Standing Desk",           "Furniture",    2,15999.00),
            ("Whiteboard 4x3 ft",       "Furniture",    7, 2200.00),
            ("Hand Sanitizer 500ml",    "Hygiene",     90,   99.00),
        ]
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        for name, category, qty, price in demo_items:
            self.inventory.append({
                "id"      : _next_id(self.inventory),
                "name"    : name,
                "category": category,
                "quantity": qty,
                "price"   : price,
                "added_on": ts,
            })
        save_data(self.inventory)
        self._refresh_table()
        self.status_var.set(f"Loaded {len(demo_items)} demo products.")

    def show_report(self):
        if not self.inventory:
            messagebox.showinfo("Report", "Inventory is empty — nothing to report.")
            return
        ReportWindow(self, self.inventory)


# ════════════════════════════════════════════════════════════════
# 5. ENTRY POINT
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()