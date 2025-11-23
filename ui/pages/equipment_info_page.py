from __future__ import annotations
from typing import List, Dict, Set, Optional
from PySide6.QtCore import Qt, QModelIndex, QPoint, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView,
                               QMessageBox, QHeaderView)
from core.models.equipment_model import EquipmentInfo
from core.logic import get_current_user
from ui.components.action_tables.equipment_table import EquipmentInfoTableModel
from ui.forms.equipment_form import EquipmentForm
from ui.components.filters.filter_proxy_models import ColumnFilterProxy
from ui.components.action_buttons.equipment_action_buttons_delegate import EquipmentActionButtonDelegate
from ui.components.dialogs.equipment_help_dialog import EquipmentHelpDialog

"""

This page defines the Equipment Info Page, the full-screen UI where users can browse, filter, import, 
add, edit, and delete equipment records. It builds a rich table interface backed by a model–proxy–delegate 
architecture, supports column-level filtering, custom action buttons, Excel importing, and context menus, 
and integrates forms for editing or creating equipment entries. The page dynamically updates its data, 
manages visibility of columns, maintains filter states, and communicates with other pages—such as navigating 
to service activity filtered by serial number. Overall, this page serves as the central hub for managing 
equipment records within the application.

ui.pages.equipment_info_page.py index:
class EquipmentInfoPage(): Main equipment management screen.
- def __init__(): Build page UI and controls.
- def _build_models(): Set up table model, proxy, and delegate.
- def load_items(): Fetch and display equipment rows.
- def _on_action_edit(): Open edit form for row.
- def _on_action_delete(): Delete a selected equipment entry.
- def _on_action_show_activity(): Jump to service log filtered by serial.
- def _on_double_click(): Open edit form on double-click.
- def open_add_form(): Open “new equipment” dialog.
- def open_edit_form(): Open filled edit dialog.
- def _apply_visible_columns(): Show/hide table columns.
- def _update_header_icons(): Add filter arrow to filtered columns.
- def _on_header_context_menu(): Open column filter popup on right-click.
- def _get_current_filtered_items(): Return items after applying active filters.
- def _actions_logical_index(): Get index of “actions” column.
- def _ensure_actions_width(): Force actions column to required width.
- def show_help_dialog(): Open equipment help modal.
"""

# Equipment Info page: The full UI page where the user views, filters, adds, edits, deletes
# equipment information.
class EquipmentInfoPage(QWidget):
    from ui.components.filters.equipment_column_filter_popup import (open_filter_window,clear_filters,
                                                              open_column_filter_popup)
    from core.importers.equipment_importer import import_from_excel
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.user = get_current_user() or "default_user"

        # Column definitions (match database fields)
        self.all_columns = [
            "id",
            "area",
            "customer",
            "building",
            "room",
            "serial_number",
            "model",
            "poc",
            "poc_phone",
            "it_support",
            "it_phone",
            "notes",
            "actions",
        ]
        self.visible_columns = list(self.all_columns)

        self.column_labels = {
            "id": "ID",
            "area": "Area",
            "customer": "Customer",
            "building": "Building",
            "room": "Room",
            "serial_number": "Serial #",
            "model": "Model",
            "poc": "POC",
            "poc_phone": "POC Phone",
            "it_support": "IT Support",
            "it_phone": "IT Phone",
            "notes": "Notes",
            "actions": "Actions",
        }

        self.active_column_filters: Dict[str, Set[str]] = {}
        self.current_items: List[EquipmentInfo] = []

        # Main layout
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)

        header = QLabel("Equipment Info")
        header.setStyleSheet("color: #ffffff; font: bold 28px 'Segoe UI';")
        root.addWidget(header, alignment=Qt.AlignLeft)

        # Control bar
        control_bar = QHBoxLayout()
        control_bar.setSpacing(8)

        # Import function
        btn_import = QPushButton("Import from Excel")
        btn_import.setFixedWidth(180)
        btn_import.clicked.connect(self.import_from_excel)
        btn_import.setCursor(QCursor(Qt.PointingHandCursor))
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

        # Add function
        btn_add = QPushButton("+ Add Equipment")
        btn_add.setFixedWidth(180)
        btn_add.clicked.connect(self.open_add_form)
        btn_add.setCursor(QCursor(Qt.PointingHandCursor))
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

        # Filters
        btn_filters = QPushButton("Filters")
        btn_filters.setFixedWidth(120)
        btn_filters.clicked.connect(self.open_filter_window)
        btn_filters.setCursor(QCursor(Qt.PointingHandCursor))
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

        # Clear all
        btn_clear = QPushButton("Clear Filters")
        btn_clear.setFixedWidth(120)
        btn_clear.clicked.connect(self.clear_filters)
        btn_clear.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)

        # Help dialog
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

        control_bar.addWidget(btn_add)
        control_bar.addWidget(btn_import)
        control_bar.addWidget(btn_filters)
        control_bar.addWidget(btn_clear)
        control_bar.addWidget(btn_help)
        control_bar.addStretch()

        root.addLayout(control_bar)

        # Main equipment list table
        self.table = QTableView()
        self.table.setMouseTracking(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)

        # Dark theme styling for consistency
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

        # Right-click on headers to filter that specific column
        header_view = self.table.horizontalHeader()
        header_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_view.customContextMenuRequested.connect(self._on_header_context_menu)

        # Edit record when double-clicking a row
        self.table.doubleClicked.connect(self._on_double_click)
        root.addWidget(self.table)

        # ID column should always be hidden (internal reference only)
        if "id" in self.visible_columns:
            self.visible_columns.remove("id")
        self._build_models()
        self.load_items()
        QTimer.singleShot(0, self._ensure_actions_width)

        # Keep fixing the actions column width when columns are resized
        self.table.horizontalHeader().sectionResized.connect(
            lambda *_: self._ensure_actions_width()
        )

    # Model / proxy / delegate setup
    def _build_models(self):
        self.base_model = EquipmentInfoTableModel([], self.all_columns, self.column_labels)
        self.proxy = ColumnFilterProxy(self.active_column_filters, self.all_columns, self)
        self.proxy.setSourceModel(self.base_model)
        self.table.setModel(self.proxy)

        # Add delegate for actions column
        try:
            actions_col = self.all_columns.index("actions")
        except ValueError:
            actions_col = -1

        if actions_col != -1:
            delegate = EquipmentActionButtonDelegate(
                parent=self.table,
                on_edit=self._on_action_edit,
                on_delete=self._on_action_delete,
                on_show_activity=self._on_action_show_activity,
            )
            self.table.setItemDelegateForColumn(actions_col, delegate)
            self._ensure_actions_width()
        self._apply_visible_columns()

    # Data loading
    def load_items(self):
        items = EquipmentInfo.get_all_for_user(self.user)
        self.current_items = items
        self.base_model.set_items(items)
        self.proxy.set_filters(self.active_column_filters)
        self._apply_visible_columns()
        self.table.resizeColumnsToContents()
        QTimer.singleShot(0, self._ensure_actions_width)

    # Action button handlers
    def _on_action_edit(self, source_row: int):
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    def _on_action_delete(self, source_row: int):
        if source_row < 0 or source_row >= len(self.base_model.items):
            return

        # Confirm deletion
        item = self.base_model.items[source_row]
        confirm = QMessageBox.question(
            self,
            "Delete Equipment",
            f"Delete equipment record for {item.customer or 'this entry'}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        EquipmentInfo.delete(item.id, self.user)
        self.load_items()

    def _on_action_show_activity(self, source_row: int):
        # When [activity] is clicked, grab serial # for that equipment record, jump to service
        # activity page, auto-apply the serial-number filter for that equipment only.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return

        equipment = self.base_model.items[source_row]
        serial = getattr(equipment, "serial_number", "").strip()

        if not serial:
            print("WARNING: Equipment has no serial number.")
            return

        # Switch page
        app = self.controller
        if not app:
            print("ERROR: No controller found on EquipmentInfoPage")
            return

        app.show_page("service_activity")

        # Once page is visible, get the page object
        sa_page = app.service_activity_page
        if not sa_page:
            print("ERROR: Could not get service_activity_page")
            return

        # Ensure service activity has a serial_number column
        col_name = "serial_number"
        if col_name not in sa_page.all_columns:
            print("ERROR: 'serial_number' column not found in SA page")
            return
        sa_page.active_column_filters[col_name] = serial

        # If SA page has a visual filter widget for Serial #, set its text
        if hasattr(sa_page, "serial_number_filter"):
            sa_page.serial_number_filter.setText(serial)
        elif hasattr(sa_page, "filter_inputs") and col_name in sa_page.filter_inputs:
            sa_page.filter_inputs[col_name].setText(serial)

        # Trigger filtering
        if hasattr(sa_page, "apply_filters"):
            sa_page.apply_filters()
        elif hasattr(sa_page, "_apply_filters"):
            sa_page._apply_filters()
        if hasattr(sa_page, "load_items"):
            sa_page.load_items()

    # Double-click to open Edit form
    def _on_double_click(self, index: QModelIndex):
        if not index.isValid():
            return

        # Convert proxy index > source index
        src_index = self.proxy.mapToSource(index)
        row = src_index.row()

        if row < 0 or row >= len(self.base_model.items):
            return

        item = self.base_model.items[row]
        self.open_edit_form(item)

    # Add/edit forms
    def open_add_form(self):
        dlg = EquipmentForm(self, item=None, on_save=self.load_items)
        dlg.exec()

    def open_edit_form(self, item: EquipmentInfo):
        dlg = EquipmentForm(self, item=item, on_save=self.load_items)
        dlg.exec()

    # Filtering + column visibility
    def _apply_visible_columns(self):
        # Hide or show columns based on self.visible_columns list
        for logical, key in enumerate(self.all_columns):
            visible = key in self.visible_columns
            self.table.setColumnHidden(logical, not visible)
        self._update_header_icons()

    # Adds small "⏷" indicator on columns with an active filter
    def _update_header_icons(self):
        for i, key in enumerate(self.all_columns):
            label = self.column_labels.get(key, key)
            if key in self.active_column_filters:
                label = f"{label} ⏷"
            self.base_model.setHeaderData(i, Qt.Horizontal, label, Qt.DisplayRole)

    # When right-clicking table header
    def _on_header_context_menu(self, pos: QPoint):
        header = self.table.horizontalHeader()
        logical = header.logicalIndexAt(pos)

        if logical < 0 or logical >= len(self.all_columns):
            return

        # Open filter popup for that exact column
        col_index = logical
        self.open_column_filter_popup(col_index)

    # Helper for filtering pipeline
    def _get_current_filtered_items(self, exclude_col: Optional[str] = None) -> List[EquipmentInfo]:
        filtered: List[EquipmentInfo] = self.base_model.items
        for col_name, allowed_set in self.active_column_filters.items():
            if exclude_col and col_name == exclude_col:
                continue
            filtered = [
                it
                for it in filtered
                if ("" if getattr(it, col_name, "") is None else str(getattr(it, col_name, "")))
                in allowed_set
            ]
        return filtered

    # Actions column width management
    def _actions_logical_index(self, width: int = 200) -> int:
        # Find index of 'actions' column in all_columns list.
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
        dlg = EquipmentHelpDialog(self)
        dlg.exec()