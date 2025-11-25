# Technician Toolkit — Technical Documentation

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![PySide6](https://img.shields.io/badge/UI-PySide6-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**Comprehensive System Architecture & Technical Documentation**

**Version:** 2025 Platform Architecture

**Author:** Brett Gildner

---

## 1. Introduction

Technician Toolkit is an enterprise-grade, offline-capable technician workflow platform designed to unify inventory management, service activity logging, equipment information access, mileage tracking, expense reporting, and parts ordering into a single modular desktop application.

The system follows a strict architectural approach that emphasizes:
 - Offline reliability
 - Clear separation of layers
 - Consistent UX patterns
 - Reusable components
 - Deterministic data flow
 - Robust synchronization rules
 - Minimal external dependencies
 - Rapid onboarding for technicians

This document covers every part of the application, including architecture, UI patterns, data models, workflow pipelines, component design, and future scalability.

---

## 2. System Overview
### 2.1 Functional Summary

Technician Toolkit provides an integrated environment for:
 - Inventory control
 - Service activity logging
 - Parts management
 - Equipment lookup
 - Mileage and expense workflows
 - Dashboard insights

### 2.2 Target Users
 - Field technicians
 - Supervisors
 - Dispatchers
 - Operations coordinators
 - Logistics and inventory managers

### 2.3 Key Requirements
 - Must work offline
 - Must run fully on local machine
 - Must provide fast and intuitive workflows
 - Must ensure data integrity
 - Must support Excel import/export templates
 - Must support table filtering, sorting, and column visibility

---

## 3. High-Level Architecture
3.1 Layered Structure
```pgsql
+---------------------------------------------------------------+
|                           Application                         |
+---------------------------------------------------------------+
| Controller Layer (app.py)                                     |
| - Routing                                                     |
| - Page management                                             |
| - Signal coordination                                         |
+---------------------------------------------------------------+
| UI Layer (ui/)                                                |
| - Pages                                                       |
| - Forms                                                       |
| - Components (tables, proxies, delegates)                     |
| - Signals                                                     |
+---------------------------------------------------------------+
| Core Layer (core/)                                            |
| - Models (SQLite-backed)                                      |
| - Importers (Excel → DB)                                      |
| - Logic (auth, init, utilities)                               |
+---------------------------------------------------------------+
| Data Layer (SQLite DB)                                        |
+---------------------------------------------------------------+
| Assets (icons, images, templates)                             |
+---------------------------------------------------------------+
```

This system is structured to ensure:
 - Predictable data flow
 - Simple debugging
 - High reusability
 - Guaranteed UI consistency
 - Strict decoupling of UI and business logic

---

## 4. Controller Layer
## ```app.py```

Acts as the central routing and refresh coordinator.

### Responsibilities
 - Initialize pages
 - Connect model-driven signals
 - Perform page switching
 - Serve as the global controller for forms
 - Provide ```refresh_*``` methods for all pages

### Signal Wiring Example
```bash
signal_bus.inventory_changed → App.refresh_inventory
signal_bus.parts_changed → App.refresh_parts
signal_bus.service_activity_changed → App.refresh_service_activity
```

The controller does not manipulate database records directly — that is the responsibility of model objects and forms.

---

## UI Layer

The UI layer is divided into four major subsystems:
1. Pages
2. Forms
3. Components
4. Signal Bus

---

## 6. Pages (Workflow Screens)
### 6.1 Service Activity Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/ServiceActivity/ServiceActivity.png" />

 - Largest workflow
 - Displays service logs using specialized table model
 - Integrates:
    - Inline editing
    - ```PartComboDelegate```
    - Column filters
    - Detailed help dialog
 - Opens ```ServiceActivityForm``` for CRUD operations
 - Automatically triggers inventory synchronization

---

### 6.2 Inventory Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/Inventory/Inventory.png" />

 - Displays inventory with color-coded toner rows
 - Supports Excel imports
 - Uses ```InventoryFilterProxy```
 - CRUD via ```InventoryForm```
 - Order workflow via ```OrderConfirmationForm```
 - Realtime updates from Service Activity signals

---

### 6.3 Equipment Information Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/EquipmentInfo/EquipmentInfo.png" />

 - Lightweight searchable table
 - Provides quick reference to equipment metadata
 - Uses EquipmentForm for editing

---

### 6.4 Mileage Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/MileageTracker/MileageTracker.png" />

 - Logs mileage entries with validation
 - Features a text-based column filter
 - Exports to formatted Excel sheet
 - Uses ```MileageForm```

---

### 6.5 Parts Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/PartsOrders/PartsOrders.png" />

 - Tracks parts orders
 - Supports exports
 - Editable entries via ```PartsOrderForm```
 - Uses ```PartsFilterProxy``` + ```PartsFilterDialog```

---

### 6.6 Expense Report Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/ExpenseReport/ExpenseReport.png" />

 - Handles monthly expense header + line items
 - Maintains editable list of expenses
 - Uses:
    - ```ExpenseHeaderDialog```
    - ```ExpenseEntryForm```
 - Exports report to Excel template

---

### 6.7 Dashboard Page
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/Dashboard/Dashboard.png" />

 - Toner level chart
 - Inventory verification countdown
 - Mileage report countdown

### 6.8 Login & Signup Pages
 - Argon2id password hashing
 - Offline verification
 - Auto-rehashing of outdated hashes

---

## 7. Forms (CRUD Dialog Layer)

All forms except ```ExpenseEntryForm``` inherit from ```BaseDialogForm```:
 - Standard Title
 - Neon-accent header
 - “Save / Cancel” layout
 - Field registry system
 - Sanitized value extraction

---

### 7.1 EquipmentForm
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/EquipmentInfo/EquipmentInfoAdd.png" />

Edits equipment metadata fields.

---

### 7.2 InventoryForm
<img width="800" height="600" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/Inventory/InventoryAdd.png" />

Creates/edits inventory item attributes.

---

### 7.3 MileageForm
<img width="500" height="500" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/MileageTracker/MileageTrackerAdd.png" />

Validates integer mileage fields and date.

---

### 7.4 PartsOrderForm
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/PartsOrders/PartsOrdersAdd.png" />

Edits customer or restock orders.

---

### 7.5 ServiceActivityForm
<img width="500" height="1400" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/ServiceActivity/ServiceActivityAdd.png" />

Most complex form:
 - Scrollable
 - Many fields
 - Date/time parsing
 - Dynamic malfunction fields
 - Automatic inventory sync on save

---

### 7.6 OrderConfirmationForm
<img width="1247" height="581" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/Inventory/InventoryOrderPopup.png" />

For converting inventory items into parts orders.

---

### 7.7 ExpenseEntryForm
<img width="200" height="500" alt="Image" src="https://github.com/brettgildner/TechnicianToolkit/blob/master/assets/screenshots/ExpenseReport/ExpenseReportAdd.png" />

Creates expense line items used only in export.

---

## 8. UI Components
### 8.1 Table System
### ```BaseTableModel```
 - Extracts data from objects
 - Applies alignment rules
 - Applies row coloring
 - Handles centerpiece column logic
 - Allows dependent overrides (e.g., toner color coding)

### ```BaseTableView```
 - Dark theme
 - Sorting
 - Row selection
 - Hover behaviors
 - Custom header styling

### 8.2 Delegates
 - Render “Edit / Delete / Order” buttons
 - Handle hover + click events
 - Map proxy rows to source model rows
 - Use custom hitboxes
 - Includes:
    - ```ActionButtonsDelegate```
    - ```InventoryActionButtonDelegate```
    - ```SAActionButtonDelegate```
    - ```EquipmentActionButtonDelegate```
    - ```PartsActionDelegate```
    - ```PartComboDelegate```

### 8.3 Filtering Framework
#### Column Filter Popups
 - Inventory
 - Equipment
 - Service Activity

Enable:
 - Checkbox filters
 - Column visibility
 - Reset tools

### ```FilterProxyModels```
Includes:
 - ```ColumnFilterProxy```
 - ```InventoryFilterProxy```
 - ```ServiceActivityFilterProxy```
 - ```MileageFilterProxy```
 - ```PartsFilterProxy```

These provide:
 - Per-column filtering
 - Global filters
 - Substring matching
 - Row-level allow/block list logic

### 8.4 Dialog System

Help dialogs for:
 - Inventory
 - Equipment
 - Mileage
 - Parts
 - Service Activity
 - Expenses

These provide user-facing documentation directly inside the app.

### 8.5 Dashboard Widget System
 - ```TonerLevelsWidget``` (PyQtGraph bar chart)
 - ```InventoryCountdownWidget```
 - ```MileageCountdownWidget```

---

## 9. Model Layer
Models provide:
 - database access
 - structure and validation
 - table initialization
 - SQL CRUD wrappers
 - signal emission

### 9.1 Standard Pattern

Each model implements:
```less
@classmethod create(...)
@classmethod update(...)
@classmethod delete(...)
@classmethod get_all()
@classmethod find(id)
@classmethod init_table()
```
### 9.2 Data Models
 - ```InventoryItem```
 - ```MileageEntry```
 - ```PartsOrder```
 - ```ExpenseLine```
 - ```ExpenseReportHeader```
 - ```EquipmentInfo```
 - ```ServiceActivity```
 - ```Category```

---

## 10. Data Integrity & Synchronization Rules
### 10.1 Service Activity → Inventory Sync
When a service activity is created, edited, or deleted:
 - Inventory quantities adjust automatically
 - Part additions subtract from inventory
 - Part deletions restore inventory
 - Part changes cause deltas (difference application)

### 10.2 Table Initialization System
During startup:
 - All tables are created if missing
 - All required columns are added
 - Type normalization is performed 

This eliminates schema drift issues.

---

## 11. Excel Import/Export Layer
### 11.1 Import Pipelines

Located in ```core/importers```.

Supported:
 - Inventory imports
 - Equipment imports
 - Service activity imports

Each importer:
 - Normalizes headers
 - Cleans values
 - Inserts or updates models

### 11.2 Export Pipelines
 - Mileage → preformatted mileage worksheet
 - Expense report → multi-section, multi-cell formatted Excel export

Exports use:
 - ```openpyxl```
 - Template-based output
 - Dynamic cell mapping

---

## 12. Security
### 12.1 Authentication Strength
 - Argon2id password hashing
 - Salted & memory-hard
 - Automatic rehashing when parameters change

### 12.2 Data Access Controls
 - User scoping applied in major models
 - Local-only storage eliminates cloud exposure

---

## 13. Performance Considerations
 - Extensive use of lightweight table models
 - Proxy models prevent unnecessary redraws
 - Database queries optimized with indexes
 - Most operations are in-memory until commit
 - 100% offline ensures zero network latency

---

## 14. Deployment Strategy
Local deployment:
 - Install Python & dependencies
 - Run ```main.py```

Planned future options:
 - PyInstaller packaging
 - Auto-update system
 - Cross-platform distributions

---

15. Testing Strategy

Recommended:
 - Unit tests for model CRUD operations
 - UI tests for page switching
 - Stress tests for large imports
 - Database schema migration tests

Not yet implemented in repository, but recommended for production.

In `assets.Forms` there is a dataset for testing (`SampleData.xlsx`).

---

16. Monitoring & Logging

Future enhancements:
 - Log file storage
 - Import/export audit logs
 - User behavior analytics

---

17. Scalability

Current system designed for:
 - Single-user offline operation

Scalable to:
 - Multi-user sync via cloud backend
 - REST API integration
 - Remote monitoring dashboards

Would require:
 - Conflict resolution
 - Sync engine
 - Auth token transformation

---

18. Roadmap
 - Undo/redo event system
 - Theme customizer
 - Bluetooth/mobile integration
 - Cloud sync option
 - Packaging into installer
 - Advanced analytics dashboard
 - UI accessibility upgrades

---

19. Appendix A — Project Structure
```bash
TechnicianToolkit
├── TechnicalDocumentation.md
├── app.py # Main controller & router
├── assets # Icons, images, templates
│   ├── Forms
│   │   ├── Expense_Report.xlsx
│   │   ├── MileageExpenseFormBlank.xlsx
│   │   └── Sample Data.xlsx
│   ├── icons
│   ├── images
│   └── screenshots
├── core
│   ├── __init__.py
│   ├── importers # Excel import tools
│   │   ├── __init__.py
│   │   ├── equipment_importer.py
│   │   ├── inventory_importer.py
│   │   └── sa_importer.py
│   ├── logic.py # Auth, table init
│   ├── models # SQLite-backed classes
│   │   ├── __init__.py
│   │   ├── category_model.py
│   │   ├── equipment_model.py
│   │   ├── expense_line_model.py
│   │   ├── expense_model.py
│   │   ├── expense_report_header_model.py
│   │   ├── inventory_model.py
│   │   ├── mileage_model.py
│   │   ├── parts_model.py
│   │   └── service_activity_model.py
│   └── utils.py
├── data
│   └── database.db # Local SQLite store
├── main.py # Entry point
└── ui
    ├── __init__.py
    ├── components # Tables, filters, delegates
    │   ├── __init__.py
    │   ├── action_buttons
    │   │   ├── __init__.py
    │   │   ├── action_buttons_delegate.py
    │   │   ├── equipment_action_buttons_delegate.py
    │   │   ├── inventory_action_buttons_delegate.py
    │   │   ├── parts_action_button_delegate.py
    │   │   └── sa_action_buttons_delegate.py
    │   ├── action_tables
    │   │   ├── __init__.py
    │   │   ├── equipment_table.py
    │   │   ├── inventory_table.py
    │   │   ├── parts_table.py
    │   │   └── service_activity_table.py
    │   ├── base_tables
    │   │   ├── __init__.py
    │   │   ├── base_table_model.py
    │   │   └── base_table_view.py
    │   ├── dialogs
    │   │   ├── __init__.py
    │   │   ├── equipment_help_dialog.py
    │   │   ├── expense_header_dialog.py
    │   │   ├── expense_help_dialog.py
    │   │   ├── inventory_help_dialog.py
    │   │   ├── mileage_help_dialog.py
    │   │   ├── parts_filter_dialog.py
    │   │   ├── parts_help_dialog.py
    │   │   └── sa_help_dialog.py
    │   ├── filters
    │   │   ├── __init__.py
    │   │   ├── equipment_column_filter_popup.py
    │   │   ├── filter_proxy_models.py
    │   │   ├── inventory_column_filter_popup.py
    │   │   └── sa_column_filter_popup.py
    │   ├── part_combo_delegate.py
    │   └── widgets.py
    ├── forms # CRUD dialogs
    │   ├── __init__.py
    │   ├── base_dialog_form.py
    │   ├── equipment_form.py
    │   ├── expense_entry_form.py
    │   ├── inventory_form.py
    │   ├── mileage_form.py
    │   ├── order_confirmation_form.py
    │   ├── parts_order_form.py
    │   └── service_activity_form.py
    ├── pages # Workflow screens
    │   ├── __init__.py
    │   ├── dashboard_page.py
    │   ├── equipment_info_page.py
    │   ├── expense_report_page.py
    │   ├── inventory_page.py
    │   ├── login_page.py
    │   ├── mileage_page.py
    │   ├── parts_page.py
    │   ├── service_activity_page.py
    │   └── signup_page.py
    └── signals # Model-driven signal bus
        ├── __init__.py
        └── model_signals.py
```
---

20. License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
