from __future__ import annotations
from typing import List, Dict
from PySide6.QtCore import Qt, QModelIndex, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableView,QMessageBox,
                               QHeaderView,QDialog)
from core.logic import get_current_user
from core.models.parts_model import PartsOrder
from ui.components.action_tables.parts_table import PartsTableModel
from ui.components.dialogs.parts_filter_dialog import PartsFilterDialog
from ui.components.dialogs.parts_help_dialog import PartsHelpDialog
from ui.components.filters.filter_proxy_models import PartsFilterProxy
from ui.forms.parts_order_form import PartsOrderForm
from ui.components.action_buttons.parts_action_button_delegate import PartsActionDelegate

"""
This page defines the PartsPage UI, a complete interface for managing parts order records, including 
viewing, filtering, adding, editing, deleting, and exporting data. It builds a styled header, control 
buttons, and a table powered by a data model, filter proxy, and action button delegate. Users can apply 
filters through a dialog, clear them, export visible records to CSV (optionally deleting them afterward), 
and open help documentation. The class also handles row-level actions such as editing or deleting orders, 
supports double-click editing, dynamically manages the actions column width, and refreshes the displayed 
data by loading all parts orders associated with the current user.

ui.pages.parts_page.py index:

class PartsPage(): The main UI component for managing parts orders.
 - def __init__(): Build UI and load data.
 - def _build_models(): Set up table model, proxy, and delegate.
 - def refresh_table(): Reload all orders into the table.
 - def open_filter_dialog(): Show filter settings dialog.
 - def clear_filters(): Remove all active filters.
 - def _on_action_edit(): Open edit form for row.
 - def _on_action_delete(): Delete selected row.
 - def _on_double_click(): Double-click to edit row.
 - def open_add_form(): Open new-order form.
 - def open_edit_form(): Open edit form for item.
 - def _actions_logical_index(): Get actions column index.
 - def _ensure_actions_width(): Resize actions column properly.
 - def export_to_csv(): Export visible rows and delete them.
 - def show_help_dialog(): Open help/instructions dialog.
"""

# Main parts page that builds the UI and manages data actions.
class PartsPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.user = get_current_user() or "default_user"

        self.columns = [
            "id",
            "part_number",
            "model",
            "description",
            "quantity",
            "actions",
        ]

        self.column_labels = {
            "id": "ID",
            "part_number": "Part Number",
            "model": "Model",
            "description": "Description",
            "quantity": "Qty",
            "actions": "Actions",
        }

        self.all_orders: List[PartsOrder] = []
        self.column_filters: Dict[int, str] = {}

        # Layout
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)

        header = QLabel("Parts Orders")
        header.setStyleSheet("color: #ffffff; font: bold 28px 'Segoe UI';")
        root.addWidget(header, alignment=Qt.AlignLeft)

        # Control Buttons
        controls = QHBoxLayout()
        controls.setSpacing(10)

        # Add order (green)
        btn_add = QPushButton("+ Add Parts Order")
        btn_add.setFixedWidth(200)
        btn_add.setCursor(QCursor(Qt.PointingHandCursor))
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #00cc55;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #00aa44;
            }
        """)
        btn_add.clicked.connect(self.open_add_form)

        # Filters (gray)
        btn_filters = QPushButton("Filters")
        btn_filters.setFixedWidth(120)
        btn_filters.setCursor(QCursor(Qt.PointingHandCursor))
        btn_filters.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        btn_filters.clicked.connect(self.open_filter_dialog)

        # Export .csv (blue)
        btn_export = QPushButton("Export CSV")
        btn_export.setFixedWidth(140)
        btn_export.setCursor(QCursor(Qt.PointingHandCursor))
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #004c99;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #003d7a;
            }
        """)
        btn_export.clicked.connect(self.export_to_csv)

        # Clear filters (red)
        btn_clear = QPushButton("Clear Filters")
        btn_clear.setFixedWidth(120)
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
        btn_clear.clicked.connect(self.clear_filters)

        # Help (orange)
        btn_help = QPushButton("Help")
        btn_help.setFixedWidth(120)
        btn_help.setCursor(QCursor(Qt.PointingHandCursor))
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: #cc6600;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #995000;
            }
        """)
        btn_help.clicked.connect(self.show_help_dialog)

        # Layout
        controls.addWidget(btn_add)
        controls.addWidget(btn_export)
        controls.addWidget(btn_filters)
        controls.addWidget(btn_clear)
        controls.addWidget(btn_help)
        controls.addStretch()
        root.addLayout(controls)

        # Table Setup
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableView {
                background-color: #1a1a1a;
                color: #e0e0e0;
                gridline-color: #333333;
                selection-background-color: #00cc88;
                alternate-background-color: #222222;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.viewport().setMouseTracking(True)

        root.addWidget(self.table, stretch=1)

        # Build model, proxy, delegate
        self._build_models()
        self.refresh_table()

    # Model / Proxy wiring
    def _build_models(self):
        # Creates the model, proxy, and action button delegate.

        self.base_model = PartsTableModel([], self.columns, self.column_labels)
        self.proxy = PartsFilterProxy(self.columns)
        self.proxy.setSourceModel(self.base_model)
        self.table.setModel(self.proxy)

        # Hide ID column from the user
        id_col = self.columns.index("id")
        self.table.setColumnHidden(id_col, True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)

        # Action buttons column
        actions_col = self.columns.index("actions")

        delegate = PartsActionDelegate(
            parent=self.table,
            on_edit=self._on_action_edit,
            on_delete=self._on_action_delete,
        )
        self.table.setItemDelegateForColumn(actions_col, delegate)
        self._ensure_actions_width()

        # Auto-size actions column
        actions_col = self._actions_logical_index()
        if actions_col != -1:
            QTimer.singleShot(0, self._ensure_actions_width)
            self.base_model.modelReset.connect(self._ensure_actions_width)
            self.base_model.layoutChanged.connect(self._ensure_actions_width)

        # Let the user resize it manually
        header.setSectionResizeMode(actions_col, QHeaderView.Interactive)
        header.resizeSection(actions_col, 180)

    # Data loading
    def refresh_table(self):
        # Get all orders for the current user and refreshes the table.
        try:
            orders = PartsOrder.get_all_for_user(self.user)
            self.all_orders = orders
            self.base_model.set_items(orders)

            # Reapply active filters
            self.proxy.set_filters(self.column_filters)

            self.table.resizeColumnsToContents()

            # Ensure actions column stays wide enough
            QTimer.singleShot(0, self._ensure_actions_width)

        except Exception as e:
            print(f"Error refreshing parts orders table: {e}")

    # Filters
    def open_filter_dialog(self):
        # Opens popup dialog to edit filters.
        dlg = PartsFilterDialog(
            self,
            self.columns,
            self.column_labels,
            self.column_filters,
        )
        if dlg.exec() == QDialog.Accepted:
            self.column_filters = dlg.get_filters()
            self.proxy.set_filters(self.column_filters)

    def clear_filters(self):
        # Removes all filters.
        self.column_filters.clear()
        self.proxy.set_filters(self.column_filters)

    # Delegate callbacks (Edit/Delete)
    def _on_action_edit(self, source_row: int):
        # Triggered when Edit button is clicked.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    def _on_action_delete(self, source_row: int):
        # Triggered when Delete button is clicked.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete parts order for part '{item.part_number}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            PartsOrder.delete(item.id)
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete record:\n{e}")

    # Double-click = edit
    def _on_double_click(self, index: QModelIndex):
        # Double-clicking a row opens the edit form.
        if not index.isValid():
            return

        source_index = self.proxy.mapToSource(index)
        source_row = source_index.row()

        if source_row < 0 or source_row >= len(self.base_model.items):
            return

        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    # Add/Edit forms
    def open_add_form(self):
        # Opens new parts order form.
        form = PartsOrderForm(self, item=None, on_save=self.refresh_table)
        form.exec()

    def open_edit_form(self, item: PartsOrder):
        # Opens edit form populated with existing data.
        form = PartsOrderForm(self, item=item, on_save=self.refresh_table)
        form.exec()

    # Actions column width helpers
    def _actions_logical_index(self) -> int:
        try:
            return self.columns.index("actions")
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

    # Export to CSV
    def export_to_csv(self):
        # Export the visible (filtered) table to CSV (and optionally delete its rows).
        try:
            from PySide6.QtWidgets import QFileDialog, QMessageBox
            import csv

            # Confirmation
            confirm = QMessageBox.question(
                self,
                "Export and Clear?",
                "Do you want to export the visible parts orders to CSV\n"
                "and then clear them from the Parts Order table?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm != QMessageBox.Yes:
                return

            # File selection
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Parts Orders CSV",
                "parts_orders.csv",
                "CSV Files (*.csv)"
            )
            if not path:
                return  # User canceled file dialog

            # Export .csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header row
                headers = [
                    self.column_labels[c]
                    for c in self.columns
                    if c not in ("id", "actions")
                ]
                writer.writerow(headers)

                # Visible rows
                ids_to_delete = []

                for row in range(self.proxy.rowCount()):
                    row_data = []
                    row_id = None

                    for col in range(self.proxy.columnCount()):
                        key = self.columns[col]
                        index = self.proxy.index(row, col)

                        # Capture ID (not exported)
                        if key == "id":
                            row_id = index.data(Qt.DisplayRole)
                            continue

                        # Skip buttons
                        if key == "actions":
                            continue

                        data = index.data(Qt.DisplayRole) or ""
                        row_data.append(data)

                    writer.writerow(row_data)

                    if row_id is not None:
                        ids_to_delete.append(int(row_id))

            # Delete exported orders
            for order_id in ids_to_delete:
                PartsOrder.delete(order_id)

            # Refresh table
            self.refresh_table()

            # Success message
            QMessageBox.information(
                self,
                "Export Complete",
                f"CSV exported successfully and {len(ids_to_delete)} orders were deleted:\n{path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error Exporting CSV", str(e))

    def show_help_dialog(self):
        dlg = PartsHelpDialog(self)
        dlg.exec()