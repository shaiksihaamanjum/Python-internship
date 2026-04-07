# Mini Inventory Management System
**Project 6 — Final Project**  
Python | tkinter | JSON | pandas (optional)

---

## Overview

A full-featured inventory tracker that simulates a real-world business utility. Supports adding, updating, deleting, and searching product records with persistent JSON storage. Available in two versions — a command-line interface (CLI) and a desktop GUI.

---

## Project Structure

```
inventory-manager/
│
├── inventory_manager.py   ← CLI version (run in terminal)
├── inventory_gui.py       ← GUI version (desktop app)
├── inventory.json         ← auto-created on first run
└── README.md              ← this file
```

---

## Requirements

- Python 3.10 or higher
- `tkinter` — built into Python, no install needed (GUI only)
- `pandas` — optional, enables full reports

Install pandas (optional):
```bash
pip install pandas
```

---

## How to Run

**CLI version:**
```bash
python inventory_manager.py
```

**GUI version:**
```bash
python inventory_gui.py
```

Both files share the same `inventory.json` file — data is always in sync between the two versions.

---

## Features

| Feature | CLI | GUI |
|---|---|---|
| View all products | Option 1 | Main table (loads on start) |
| Add a new product | Option 2 | "Add Product" button |
| Update a product | Option 3 | Double-click row / "Edit Selected" |
| Delete a product | Option 4 | "Delete Selected" button |
| Search products | Option 5 | Search box + Category filter |
| Generate report | Option 6 | "Report" button |
| Load demo data | Option 7 | "Load Demo Data" button |
| Clear all data | Option 8 | "Clear All Data" button |

---

## Product Fields

Each inventory item stores the following fields:

| Field | Description |
|---|---|
| `id` | Unique permanent ID (never changes after deletion) |
| `name` | Product name |
| `category` | Product category (e.g. Electronics, Stationery) |
| `quantity` | Units in stock |
| `price` | Unit price in Rs. |
| `added_on` | Timestamp when product was added |
| `updated_on` | Timestamp of last update (if edited) |

---

## Data Storage

All data is saved in `inventory.json` in the same folder as the scripts. The file is created automatically on first run and updated after every add, edit, or delete operation. No database setup is required.

Example record in `inventory.json`:
```json
{
    "id": 1,
    "name": "Wireless Mouse",
    "category": "Electronics",
    "quantity": 45,
    "price": 599.0,
    "added_on": "2025-01-01 10:00"
}
```

---

## Report Feature

The report shows:
- Total distinct products
- Total units in stock
- Total inventory value
- Average unit price (pandas only)
- Most expensive item (pandas only)
- Lowest stock item (pandas only)
- Category-wise breakdown
- Low stock alert (items with quantity below 5)

If pandas is not installed, a basic report is shown using manual calculations.

---

## Concepts & Skills Demonstrated

- **CRUD operations** — Create, Read, Update, Delete
- **File I/O** — JSON persistence using Python's built-in `json` module
- **Input validation** — all user inputs are validated before saving
- **Menu-driven interface** — numbered options in CLI, buttons in GUI
- **Modular code** — each feature is a separate function
- **OOP** — GUI built using tkinter classes (`InventoryApp`, `ProductDialog`, `ReportWindow`)
- **pandas integration** — optional data analytics and reporting
- **S.No vs ID** — display row count separately from permanent product ID

---

## GUI Extra Features

- Click any column header to sort the table
- Rows with quantity below 5 are highlighted in red
- Live stats bar showing totals at the top
- Status bar at the bottom showing last action
- Double-click any row to edit it

---

## Notes

- Deleting a product does not change existing IDs — this is intentional (same as real databases)
- The S.No column in the table always resets to 1, 2, 3... after a deletion
- The "Clear All Data" option requires typing `YES` (case-insensitive) to confirm
- Demo data can only be loaded into an empty inventory — clear first if needed