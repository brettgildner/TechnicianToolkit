from __future__ import annotations
from typing import List, Dict, Set, Optional
from PySide6.QtCore import Qt, QModelIndex, QPoint, QTimer
from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableView,QMessageBox,
                               QMenu,QHeaderView)
from core.logic import get_current_user, compute_duration
from core.models.service_activity_model import ServiceActivity
from ui.components.action_tables.service_activity_table import ServiceActivityTableModel
from ui.components.dialogs.sa_help_dialog import ServiceActivityHelpDialog
from ui.forms.service_activity_form import ServiceActivityForm
from ui.components.part_combo_delegate import PartComboDelegate
from ui.components.action_buttons.sa_action_buttons_delegate import SAActionButtonDelegate
from ui.components.filters.filter_proxy_models import ServiceActivityFilterProxy

"""
This page implements the full Service Activity management interface, providing tools to view, filter, 
add, edit, import, and delete service activity records. It includes a sortable, filterable table powered 
by a model, proxy, and several custom delegates, including dropdowns for part selection and row-level 
action buttons. The page manages complex behaviors such as dynamic column visibility, header-based filter 
popups, context menus, record deletion with automatic inventory replenishment, and Excel import 
functionality. It also recalculates call durations, maintains active filters, and updates other 
application pages when changes occur. Overall, it serves as the central hub for handling all 
service-activity-related data in the application’s UI.

ui.pages.service_activity_page.py index:
class ServiceActivityPage(): Main UI for service activity records.
 - def __init__(): Build full UI + toolbar + table.
 - def _build_models(): Set up model, proxy, and delegates.
 - def _on_proxy_data_changed(): Handle proxy data updates.
 - def load_items(): Load service activities from DB.
 - def _apply_visible_columns(): Show/hide selected columns.
 - def _update_header_icons(): Mark filtered columns in header.
 - def _on_table_context_menu(): Right-click edit/delete menu.
 - def _on_double_click(): Double-click to edit row.
 - def _on_action_edit(): Edit row from action button.
 - def _on_action_delete(): Delete row from action button.
 - def edit_selected(): Edit currently selected row.
 - def delete_selected(): Delete selected row.
 - def _do_delete(): Perform delete + restock inventory.
 - def _on_header_context_menu(): Header right-click column filter.
 - def _get_current_filtered_items(): Items passing active filters.
 - def open_add_form(): Open new activity form.
 - def open_edit_form(): Open edit form.
 - def _actions_logical_index(): Find actions column index.
 - def _ensure_actions_width(): Resize actions column.
 - def show_help_dialog(): Open help window.
"""

# Main page for displaying, filtering, editing, and importing service activity entries.
class ServiceActivityPage(QWidget):
    # The main "Service Activity" screen the user interacts with. It owns the toolbar
    # buttons, the QTableView where entries are listed, the model, proxy, and delegate,
    # and the logic for loading data, opening forms, and deleting records.
    from ui.components.filters.sa_column_filter_popup import (open_filter_window,clear_filters,
                                                              open_column_filter_popup)
    from core.importers.sa_importer import import_from_excel

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        # Import DB path
        self.inventory_page = None
        import os
        self.db_path = os.path.join("data", "database.db")

        # Reference to main window controller
        self.controller = controller
        self.user = get_current_user() or "default_user"

        # Column definitions
        self.all_columns: List[str] = [
            "id",
            "area",
            "customer",
            "serial_number",
            "meter",
            "malfunction",
            "arrival_date",
            "arrival_time",
            "remedial_action",
            "quantity",
            "part_replaced",
            "departure_date",
            "departure_time",
            "call_duration",
            "technician",
            "comments",
            "actions",
        ]

        self.visible_columns: List[str] = list(self.all_columns)
        # Debug
        print("DEBUG: Using DB:", os.path.abspath(self.db_path))

        self.column_labels: Dict[str, str] = {
            "id": "ID",
            "area": "Area",
            "customer": "Customer",
            "serial_number": "Serial #",
            "meter": "Meter",
            "malfunction": "Malfunction",
            "arrival_date": "Arrival Date",
            "arrival_time": "Arrival Time",
            "remedial_action": "Remedial Action Performed",
            "quantity": "Qty",
            "part_replaced": "Part Replaced",
            "departure_date": "Departure Date",
            "departure_time": "Departure Time",
            "call_duration": "Duration",
            "technician": "Technician",
            "comments": "Comments",
            "actions": "Actions",
        }

        self.active_column_filters: Dict[str, Set[str]] = {}
        self.current_items: List[ServiceActivity] = []

        # Page layout (header + toolbar + table)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)

        # Page header
        header = QLabel("Service Activity")
        header.setStyleSheet("color: #ffffff; font: bold 28px 'Segoe UI';")
        root.addWidget(header, alignment=Qt.AlignLeft)

        # Toolbar: Add / Import / Filters / Clear
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Button definitions

        # Import (Bright Blue)
        btn_import = QPushButton("Import from Excel")
        btn_import.setFixedWidth(180)
        btn_import.clicked.connect(self.import_from_excel)
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #008cff;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0077dd;
            }
        """)

        # Add (Green)
        btn_add = QPushButton("+ Add Service Activity")
        btn_add.setFixedWidth(220)
        btn_add.clicked.connect(self.open_add_form)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #00cc55;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #00aa44;
            }
        """)

        # Filters (Gray)
        btn_filters = QPushButton("Filters")
        btn_filters.setFixedWidth(120)
        btn_filters.clicked.connect(self.open_filter_window)
        btn_filters.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        # Clear Filters (Red)
        btn_clear = QPushButton("Clear Filters")
        btn_clear.setFixedWidth(120)
        btn_clear.clicked.connect(self.clear_filters)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)

        # Help (Dark Orange)
        btn_help = QPushButton("Help")
        btn_help.setFixedWidth(100)
        btn_help.clicked.connect(self.show_help_dialog)
        btn_help.setCursor(QCursor(Qt.PointingHandCursor))
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: #cc6600;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #995000;
            }
        """)

        # Set cursors
        for b in (btn_import, btn_add, btn_filters, btn_clear, btn_help):
            b.setCursor(QCursor(Qt.PointingHandCursor))

        # Add to toolbar
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_import)
        toolbar.addWidget(btn_filters)
        toolbar.addWidget(btn_clear)
        toolbar.addWidget(btn_help)
        toolbar.addStretch()

        root.addLayout(toolbar)

        # Table
        self.table = QTableView()
        self.table.setEditTriggers(QTableView.AllEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableView {
                background-color: #1a1a1a;
                color: #e0e0e0;
                gridline-color: #333;
                selection-background-color: #00cc88;
                alternate-background-color: #222;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #fff;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_table_context_menu)

        self.table.doubleClicked.connect(self._on_double_click)
        self.table.setSortingEnabled(True)

        header_view = self.table.horizontalHeader()
        header_view.setContextMenuPolicy(Qt.CustomContextMenu)
        header_view.customContextMenuRequested.connect(self._on_header_context_menu)
        header_view.setSectionsMovable(False)

        root.addWidget(self.table)

        # Model + proxy + delegate
        self._build_models()
        self.load_items()
        # Debug: check flags AFTER rows exist
        try:
            part_col = self.all_columns.index("part_replaced")
            #print("\nDEBUG: Checking flags on REAL rows:")
            #print("DEBUG: part_col =", part_col)

            for r in range(self.base_model.rowCount()):
                idx = self.base_model.index(r, part_col)
                #print(f" - Row {r}: flags =", self.base_model.flags(idx))

        except Exception as e:
            #print("DEBUG ERROR while checking flags:", e)
            pass

    # Model wiring (model + proxy + delegate)
    def _build_models(self):
        # Base model
        self.base_model = ServiceActivityTableModel(
            [], self.all_columns, self.column_labels
        )

        # Proxy
        self.proxy = ServiceActivityFilterProxy(
            self.active_column_filters, self.all_columns
        )
        self.proxy.setSourceModel(self.base_model)

        # Attach proxy to table
        self.table.setModel(self.proxy)

        # Determine part_replaced column
        try:
            part_col = self.all_columns.index("part_replaced")
        except ValueError:
            part_col = -1

        #print("DEBUG: part_col =", part_col)

        # Connect PROXY > wrapper
        self.proxy.dataChanged.connect(self._on_proxy_data_changed)
        #print("DEBUG: Connected dataChanged to _on_proxy_data_changed")

        # Install PartComboDelegate
        if part_col != -1:
            delegate = PartComboDelegate(self.db_path, parent=self.table)
            self.table.setItemDelegateForColumn(part_col, delegate)
            #print("DEBUG: Installed PartComboDelegate")

        # Actions delegate
        actions_col = self._actions_logical_index()
        if actions_col != -1:
            delegate = SAActionButtonDelegate(
                parent=self.table,
                on_edit=self._on_action_edit,
                on_delete=self._on_action_delete,
            )
            self.table.setItemDelegateForColumn(actions_col, delegate)
            self._ensure_actions_width()

        # Hide ID column and apply visibility
        if "id" in self.visible_columns:
            self.visible_columns.remove("id")

        self._apply_visible_columns()

    def _on_proxy_data_changed(self, topLeft, bottomRight, roles):
        # Currently no behavior needed here.
        pass

    # Data loading
    def load_items(self):
        # Load all ServiceActivity records for the current user from the database,
        # compute call_duration if missing, and pushes them into the table model.

        items = ServiceActivity.get_all_for_user(self.user)

        # Attach the controller (App) to every ServiceActivity
        # so SA.update() can refresh inventory correctly.
        for sa in items:
            sa.controller = self.controller

        # Ensure call_duration is filled if missing
        for act in items:
            act.call_duration = compute_duration(
                act.arrival_date,
                act.arrival_time,
                act.departure_date,
                act.departure_time,
            )

        self.current_items = items
        self.base_model.set_items(items)
        self.proxy.set_filters(self.active_column_filters)
        self._apply_visible_columns()
        self.table.resizeColumnsToContents()
        QTimer.singleShot(0, self._ensure_actions_width)

    # Column visibility + header icons
    def _apply_visible_columns(self):
        #Show/hide columns based on self.visible_columns.
        for logical, key in enumerate(self.all_columns):
            visible = key in self.visible_columns
            self.table.setColumnHidden(logical, not visible)

        # Update header texts (Add "⏷" on columns that have active filters).
        self._update_header_icons()

    def _update_header_icons(self):
        # Adds a "⏷" in the header text for columns that currently have active filters.
        for i, key in enumerate(self.all_columns):
            label = self.column_labels.get(key, key)
            if key in self.active_column_filters:
                label = f"{label} ⏷"
            self.base_model.setHeaderData(i, Qt.Horizontal, label, Qt.DisplayRole)

    # Context menu (right-click on table rows)
    def _on_table_context_menu(self, pos: QPoint):
        # Shows a small 'Edit'/'Delete' menu when the user right-clicks on a row.
        index = self.table.indexAt(pos)
        menu = QMenu(self)

        # Edit: same as double-click or pressing the Edit button.
        act_edit = QAction("Edit", self)
        act_edit.triggered.connect(lambda: self.edit_selected(index))
        menu.addAction(act_edit)

        # Delete: ask for confirmation and remove the record.
        act_delete = QAction("Delete", self)
        act_delete.triggered.connect(lambda: self.delete_selected(index))
        menu.addAction(act_delete)

        # Show the menu at the correct global screen location.
        menu.exec(self.table.viewport().mapToGlobal(pos))

    # Row events: double-click / delegate callbacks
    def _on_double_click(self, index: QModelIndex):
        # Double-clicking a row opens ServiceActivityForm for editing.
        if not index.isValid():
            return
        # Map from proxy row to source row.
        source_row = self.proxy.mapToSource(index).row()
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    # Delegate calls below pass "source_row", already mapped back to base model
    def _on_action_edit(self, source_row: int):
        # Called by the delegate when the "Edit" button is clicked for a row.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    def _on_action_delete(self, source_row: int):
        # Called by the delegate when the "Delete" button is clicked for a row.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self._do_delete(item)

    # Edit/delete helpers (using currently selected row)
    def edit_selected(self, index: Optional[QModelIndex] = None):
        # Edits the currently selected row; if no index is explicitly provided, like
        # from the context menu, use the table's current selection.
        if index is None or not index.isValid():
            idx = self.table.currentIndex()
            if not idx.isValid():
                return
            index = idx

        source_row = self.proxy.mapToSource(index).row()
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    def delete_selected(self, index: Optional[QModelIndex] = None):
        # Delete the current row; If none provided, rely on the table's selected row.
        if index is None or not index.isValid():
            idx = self.table.currentIndex()
            if not idx.isValid():
                return
            index = idx

        source_row = self.proxy.mapToSource(index).row()
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self._do_delete(item)

    def _do_delete(self, item: ServiceActivity):
        # Delete the service activity and restore associated inventory usage.
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete service activity for {getattr(item, 'customer', 'this record')}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            # 1. Restore inventory before deleting the SA record
            part = getattr(item, "part_replaced", "").strip()
            qty = int(getattr(item, "quantity", 0))

            if part and qty > 0:
                from core.models.inventory_model import InventoryItem
                InventoryItem.add_quantity(part, qty)  # <-- replenish stock

            # 2. Delete the ServiceActivity record
            item.delete()

            # 3. Reload SA table
            self.load_items()

            # 4. Refresh inventory page if visible
            if getattr(self.controller, "inventory_page", None):
                self.controller.inventory_page.load_items()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete record: {e}")

    # Header right-click: per-column filter popup
    def _on_header_context_menu(self, pos: QPoint):
        # Right-click shows the filter popup for that specific column.
        header = self.table.horizontalHeader()
        logical = header.logicalIndexAt(pos)
        if logical < 0 or logical >= len(self.all_columns):
            return
        col_index = logical
        self.open_column_filter_popup(col_index)

    def _get_current_filtered_items(
        self,
        exclude_col: Optional[str] = None
    ) -> List[ServiceActivity]:
        # Returns a list of items that pass all active filters & optionally ignores a specific
        # columns filter (so the popup sees all values for the column being changed.
        filtered = self.base_model.items
        for col_name, allowed_set in self.active_column_filters.items():
            if exclude_col and col_name == exclude_col:
                continue
            filtered = [
                it
                for it in filtered
                if ("" if getattr(it, col_name, "") is None
                    else str(getattr(it, col_name, ""))) in allowed_set
            ]
        return filtered

    # Forms (Add / Edit)
    def open_add_form(self):
        # Opens new ServiceActivityForm for a new record, the form calls self.load_items()
        # after saving (via on_save()), table refreshes automatically.
        dlg = ServiceActivityForm(self, on_save=self.load_items, item=None)
        dlg.exec()

    def open_edit_form(self, item: ServiceActivity):
        # Open a ServiceActivityForm pre-filled with an existing record for editing.
        dlg = ServiceActivityForm(
            self,
            on_save=self.load_items,
            item=item
        )
        dlg.exec()

    # Actions column width helpers
    def _actions_logical_index(self) -> int:
        # Return index of 'actions' column in all_columns; returns -1 if not present.
        try:
            return self.all_columns.index("actions")
        except ValueError:
            return -1

    def _ensure_actions_width(self):
        # Ensures the actions column width matches the delegate's requirements.
        li = self._actions_logical_index()
        if li < 0:
            return

        header = self.table.horizontalHeader()

        # Determine correct width from delegate
        delegate = self.table.itemDelegateForColumn(li)
        if hasattr(delegate, "required_width"):
            width = delegate.required_width()
        else:
            width = 220

        header.setSectionResizeMode(li, QHeaderView.ResizeMode.Interactive)

        # Enforce proper width
        if header.sectionSize(li) < width:
            header.resizeSection(li, width)

    def show_help_dialog(self):
        dlg = ServiceActivityHelpDialog(self)
        dlg.exec()
