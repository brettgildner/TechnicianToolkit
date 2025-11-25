# Technician Toolkit

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![PySide6](https://img.shields.io/badge/UI-PySide6-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A modular, offline-capable desktop application built with PySide6 for field technicians.
It consolidates inventory management, service activity logging, mileage tracking, expense 
reporting, equipment information, and parts ordering into a single unified interface backed 
by a local SQLite database.

The system features a reusable UI component framework, a model-driven signal bus, Excel 
import/export utilities, and a dark-themed polished UI.

---

## Table of Contents
 - Overview
 - Key Features
 - Screenshots
 - Installation
 - Running the App
 - Project Structure
 - Architecture
 - UI Framework
 - Database Models
 - Excel Import/Export
 - License

---

## Overview

The Technician Toolkit acts as a centralized workspace for technicians, replacing 
spreadsheets and scattered tools with a robust, cohesive desktop environment.

Built with PySide6 (Qt for Python) and designed for offline use, it supports:

 - Secure authentication
 - Inventory tracking with automatic synchronization
 - Service activity logging with part usage integration
 - Mileage tracking with template export
 - Expense reporting
 - Equipment information management
 - Parts ordering
 - Dashboard analytics and status widgets

---

## Key Features

### Authentication
 - Secure login & signup | Argon2id password hashing
 - Fully offline authentication | User-specific data isolation

### Inventory Management
 - Track part numbers, quantities, categories | Inline editing | Excel imports
 - Column filtering & visibility controls | Automatic sync with Service Activity part usage

### Service Activity Log
 - Customer, area, equipment, malfunction, timestamps | Duration automatically calculated
 - Add/remove parts and quantities | Full filtering system with column popups
 - Excel import support | Automatic inventory adjustments (additions, deletions, updates)

### Equipment Information
 - Searchable table | Column filtering & actions | Edit and delete equipment records

### Mileage Tracker
 - Add/edit/delete mileage entries | Filter by text, date range, or column filters
 - Computed “miles driven” column | Export to preformatted Excel mileage template

### Expense Reporting
 - Maintain a monthly expense report header | Add multiple expense line items
 - Export to Excel expense form template | Supports mileage and itemized entries

### Parts Ordering
 - Records routine restock and/or customer-requested orders | Filterable table
 - CSV export with optional deletion | Integrated editor & confirmation form

### Dashboard
 - Toner level visualization | Inventory verification countdown | Mileage deadline countdown

---
## Screenshots


| **Dashboard** | **Service Activity** |
|----------|------------------|
| <img src="https://raw.githubusercontent.com/brettgildner/TechnicianToolkit/master/assets/screenshots/Dashboard/Dashboard.png" width="400"> | <img src="https://raw.githubusercontent.com/brettgildner/TechnicianToolkit/master/assets/screenshots/ServiceActivity/ServiceActivity.png" width="400"> |
| *Toner levels, deadlines, and quick-action buttons* | *Logged service calls with timestamps, parts, and details* |

<br>

| **Inventory** | **Expense Report** |
|----------|----------------|
| <img src="https://raw.githubusercontent.com/brettgildner/TechnicianToolkit/master/assets/screenshots/Inventory/Inventory.png" width="400"> | <img src="https://raw.githubusercontent.com/brettgildner/TechnicianToolkit/master/assets/screenshots/ExpenseReport/ExpenseReport.png" width="400"> |
| *Part tracking, verification dates, and a 'quick-order' function* | *Monthly expense header + itemized entries with export* |


---

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/brettgildner/TechnicianToolkit.git

cd TechnicianToolkit
```
### 2. Create & activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
---

## Running the App
```bash
python main.py
```
On first launch:
 - Database tables initialize automatically
 - Login window appears
 - Sidebar unlocks after authentication

---

## Project Structure
```css
TechnicianToolkit/
├── app.py
├── main.py
├── assets/
│   ├── Forms/
│   ├── icons/
│   └── images/
├── core/
│   ├── importers/
│   ├── models/
│   ├── logic.py
│   └── utils.py
├── data/
│   └── database.db
└── ui/
    ├── components/
    ├── forms/
    ├── pages/
    └── signals/
```
---

## Architecture
Technician Toolkit uses a hybrid MVC-style architecture with:
 - Models → SQLite-backed classes with CRUD methods
 - Views → PySide6 pages, dialogs, and widgets
 - Controllers → The `App` object, refresh orchestrator, and page router
 - Signal Bus → Centralized model signals to refresh UI automatically
 - Reusable Component Framework → Tables, delegates, popups, proxy models

---

## UI Framework
### Base Components
 - ```BaseTableModel``` — Data extraction, alignment, formatting
 - ```BaseTableView``` — Dark-themed, sortable table view
 - Action Buttons Delegates — Edit/Delete/Order in-table buttons
 - Filter Proxy Models — Custom filtering logic
 - Column Filter Popups — Column checkboxes & visibility
 - Dashboard Widgets — Aggregations + charts

### Forms
All CRUD dialogs use:
 - ```BaseDialogForm``` (except ```ExpenseEntryForm```)
 - Uniform layout
 - Validations
 - Model save + callback

### Pages
Each page wraps:
 - Toolbar | Table view | Filter logic | CRUD operations | Help dialog

---

## Database Models

Models include:
 - ```InventoryItem``` | ```ServiceActivity``` | ```EquipmentInfo``` | ```MileageEntry```
 - ```PartsOrder``` | ```ExpenseReportInfo``` | ```ExpenseLine``` | ```Category```

All models:
 - Auto-create tables
 - Validate columns on startup
 - Normalize string & numeric fields
 - Use user isolation where applicable

Automatic inventory sync occurs in the ServiceActivity model.

---

## Excel Import/Export
Importers

Located in `core/importers`
 - `equipment_importer.py`
 - `inventory_importer.py`
 - `sa_importer.py`

Exporters
 - Mileage export → Prestructured mileage form template
 - Expense report export → Excel form with line items

All use `openpyxl`.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
