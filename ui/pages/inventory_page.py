from __future__ import annotations
from typing import List, Dict, Any, Set, Optional
from PySide6.QtCore import (Qt, QModelIndex, QPoint, QTimer)
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QMessageBox,
                               QDialog, QDialogButtonBox, QLineEdit, QTextEdit,QGridLayout,
                               QHeaderView,QTableView)
from core.logic import get_current_user
from core.models.inventory_model import InventoryItem
from core.models.parts_model import PartsOrder
from ui.components.action_tables.inventory_table import InventoryTableModel
from ui.components.dialogs.inventory_help_dialog import InventoryHelpDialog
from ui.forms.inventory_form import InventoryForm
from ui.components.action_buttons.inventory_action_buttons_delegate import InventoryActionButtonDelegate
from ui.components.filters.filter_proxy_models import InventoryFilterProxy

"""
The Inventory Page provides the full user interface for viewing, filtering, adding, editing, deleting, 
and ordering inventory parts. It displays inventory items in a sortable and filterable table with an 
actions column that includes edit, delete, and order buttons. It also supports importing items from Excel, 
applying complex column filters, using right-click context menus, and triggering updates throughout the 
app. The page manages communication with the database, handles dialogs like the order popup and add/edit 
forms, and keeps the UI synced with model changes to maintain an organized and efficient workflow for 
inventory management.

ui.pages.inventory_page.py index:

class TemporaryInfoDialog: Simple “OK only” message popup.
 - def __init__(): Create small informational dialog.
class OrderPopup: Dialog to order a part.
 - def __init__(): Build order form UI.
 - def _submit(): Validate and return order qty/notes.
class InventoryPage: Main inventory management screen.
 - def __init__(): Build entire inventory page UI.
 - def _build_models(): Prepare data model, filter proxy, and action delegate.
 - def load_items(): Load inventory from database.
 - def _apply_visible_columns(): Show/hide columns based on settings.
 - def _update_header_icons(): Add filter indicators to headers.
 - def _on_table_context_menu(): Right-click row > delete/order menu.
 - def _on_double_click(): Double-click row > edit item.
 - def _on_action_order(): Handle “Order” button click.
     - def on_submit(): Finish order creation.
 - def _on_action_edit(): Handle “Edit” button click.
 - def _on_action_delete(): Handle “Delete” button click.
 - def delete_selected(): Delete currently selected item.
 - def order_selected(): Order currently selected item.
 - def _on_header_context_menu(): Right-click header > column filter popup.
 - def _get_current_filtered_items(): Return items passing active filters.
 - def open_add_form(): Open new inventory item form.
 - def open_edit_form(): Open edit inventory item form.
 - def _after_save(): Refresh data and notify other pages.
 - def import_from_excel(): Import inventory from an Excel sheet.
 - def _actions_logical_index(): Locate “Actions” column index.
 - def _ensure_actions_width(): Force correct width for action buttons.
 - def show_help_dialog(): Open help information dialog.
"""

class TemporaryInfoDialog(QDialog):
# Simple “OK only” message popup.
    def __init__(self, title: str, text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(text))
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        lay.addWidget(btns)


class OrderPopup(QDialog):
# Dialog to order a part.
    def __init__(self, parent, item, on_submit):
        super().__init__(parent)
        self.item = item
        self.on_submit = on_submit
        self.setWindowTitle("Order Part")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        # Title with part number
        title = QLabel(f"Order Part: {item.part_number}")
        title.setStyleSheet("font: bold 18px 'Segoe UI';")
        layout.addWidget(title)

        # Description of the part
        desc = QLabel(f"Description: {item.part_description or '(no description)'}")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Form layout for quantity + notes
        form = QGridLayout()
        form.addWidget(QLabel("Quantity to Order:"), 0, 0)
        self.qty_edit = QLineEdit(str(item.quantity or 1))
        self.qty_edit.setFixedWidth(120)
        form.addWidget(self.qty_edit, 0, 1)

        form.addWidget(QLabel("Notes (optional):"), 1, 0, Qt.AlignTop)
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(90)
        form.addWidget(self.notes_edit, 1, 1)
        layout.addLayout(form)

        # OK / Cancel buttons
        btns = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        btns.button(QDialogButtonBox.Ok).setText("Confirm Order")
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self._submit)
        layout.addWidget(btns)

    def _submit(self):
    # Validate the quantity, then call the on_submit callback and close the dialog.

        qty_str = self.qty_edit.text().strip()
        notes = self.notes_edit.toPlainText().strip()
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a positive integer for quantity.")
            return

        self.on_submit(qty, notes)
        self.accept()

class InventoryPage(QWidget):
# Inventory Page (main screen); the actual page the user interacts with via buttons ('add',
# 'filters', etc), table + actions column, right-click menu, double-click edit, filter
# dialogs, and the Excel import.
    from ui.components.filters.sa_column_filter_popup import open_filter_window, clear_filters
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.user = get_current_user() or "default_user"

        self.all_columns = [
            "part_number",
            "quantity",
            "part_location",
            "model",
            "part_description",
            "quarterly_inventory_verification_date",
            "days_since_verification",
            "category_id",
            "actions",
        ]

        self.visible_columns = list(self.all_columns)

        self.column_labels = {
            "part_number": "Part #",
            "quantity": "Qty",
            "part_location": "Location",
            "model": "Model",
            "part_description": "Description",
            "quarterly_inventory_verification_date": "Verified",
            "days_since_verification": "Days",
            "category_id": "Category",
            "actions": "Actions",
        }

        self.active_column_filters: Dict[str, Set[str]] = {}
        self.current_items: List[Any] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)

        header = QLabel("Inventory")
        header.setStyleSheet("color: #ffffff; font: bold 28px 'Segoe UI';")
        root.addWidget(header, alignment=Qt.AlignLeft)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        btn_import = QPushButton("Import from Excel")
        btn_import.setFixedWidth(180)
        btn_import.clicked.connect(self.import_from_excel)
        btn_import.setCursor(QCursor(Qt.PointingHandCursor))
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #0088ff;
                color: #ffffff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #1a9dff;
            }
        """)

        btn_add = QPushButton("+ Add Inventory Item")
        btn_add.setFixedWidth(200)
        btn_add.clicked.connect(self.open_add_form)
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

        btn_filters = QPushButton("Filters")
        btn_filters.setFixedWidth(120)
        btn_filters.clicked.connect(self.open_filter_window)
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

        btn_help = QPushButton("Help")
        btn_help.setFixedWidth(100)
        btn_help.clicked.connect(self.show_help_dialog)
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

        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_import)
        toolbar.addWidget(btn_filters)
        toolbar.addWidget(btn_clear)
        toolbar.addWidget(btn_help)
        toolbar.addStretch()
        root.addLayout(toolbar)

        self.table = QTableView()
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

        header_view = self.table.horizontalHeader()
        header_view.setContextMenuPolicy(Qt.CustomContextMenu)
        header_view.customContextMenuRequested.connect(self._on_header_context_menu)
        root.addWidget(self.table)

        self._build_models()
        self.load_items()
        from ui.signals.model_signals import model_signals
        model_signals.inventory_changed.emit()

    # Create the base model (data), the filter proxy (hides rows), and attach the action
    # button delegate to the "Actions" column.
    def _build_models(self):
        self.base_model = InventoryTableModel([], self.all_columns, self.column_labels)
        self.proxy = InventoryFilterProxy(self.active_column_filters, self.all_columns)
        self.proxy.setSourceModel(self.base_model)
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)

        actions_col = self._actions_logical_index()
        if actions_col != -1:
            delegate = InventoryActionButtonDelegate(
                parent=self.table,
                on_order=self._on_action_order,
                on_edit=self._on_action_edit,
                on_delete=self._on_action_delete
            )
            self.table.setItemDelegateForColumn(actions_col, delegate)
            self._ensure_actions_width()

            header = self.table.horizontalHeader()
            last_col = len(self.all_columns) - 1
            if actions_col != last_col:
                header.moveSection(actions_col, last_col)

            header.setStretchLastSection(False)
            header.setSectionsMovable(False)
            QTimer.singleShot(0, self._ensure_actions_width)

            self.base_model.modelReset.connect(self._ensure_actions_width)
            self.base_model.layoutChanged.connect(self._ensure_actions_width)

        if "id" in self.visible_columns:
            self.visible_columns.remove("id")

        self._apply_visible_columns()
        self.table.viewport().setMouseTracking(True)

    # Load data from db - called at startup and after operations like add/edit/delete/import.
    def load_items(self):
        items = InventoryItem.get_all_for_user(self.user)
        self.current_items = items
        self.base_model.set_items(items)
        self.proxy.set_filters(self.active_column_filters)
        self._apply_visible_columns()
        self.table.resizeColumnsToContents()
        QTimer.singleShot(0, self._ensure_actions_width)

    # Column visibility + header labels
    def _apply_visible_columns(self):
        for logical, key in enumerate(self.all_columns):
            visible = key in self.visible_columns
            self.table.setColumnHidden(logical, not visible)
        self._update_header_icons()

    def _update_header_icons(self):
        for i, key in enumerate(self.all_columns):
            label = self.column_labels.get(key, key)
            if key in self.active_column_filters:
                label = f"{label} ⏷"
            self.base_model.setHeaderData(i, Qt.Horizontal, label, Qt.DisplayRole)

    # Table body right-click menu; when the user right-clicks inside the table rows, show a small menu
    # with "Delete Item" and "Order Item" options.
    def _on_table_context_menu(self, pos: QPoint):
        index = self.table.indexAt(pos)
        menu = QMenu(self)

        act_delete = QAction("Delete Item", self)
        act_delete.triggered.connect(lambda: self.delete_selected(index))
        menu.addAction(act_delete)

        act_order = QAction("Order Item", self)
        act_order.triggered.connect(lambda: self.order_selected(index))
        menu.addAction(act_order)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    # Double-click anywhere on a row (except buttons) to open the edit dialog.
    def _on_double_click(self, index: QModelIndex):
        if not index.isValid():
            return
        # Map from proxy (sorted/filtered view) back to original data row.
        source_row = self.proxy.mapToSource(index).row()
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    # Delegate button callbacks (order/edit/delete); called by ActionButtonDelegate when a
    # mini-button is clicked. source_row refers to the row index in the base model (not filtered).
    def _on_action_order(self, source_row: int):
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]

        # Define what happens when the user confirms an order in the OrderPopup.
        def on_submit(qty, notes):
            # Create a new PartsOrder record in the database.
            PartsOrder.create(
                quantity=qty,
                part_number=item.part_number,
                model=item.model,
                description=item.part_description,
                user=self.user,
            )
            QMessageBox.information(
                self,
                "Order Created",
                f"Ordered {qty}x '{item.part_number}' successfully."
            )

            # Immediately refresh PartsPage if it exists
            if hasattr(self.controller, "parts_page") and self.controller.parts_page:
                try:
                    self.controller.parts_page.refresh_table()
                except Exception as e:
                    print(f"Failed to refresh PartsPage automatically: {e}")

        dlg = OrderPopup(self, item, on_submit)
        dlg.exec()

    def _on_action_edit(self, source_row: int):
        # Called when clicking 'Edit' in 'Actions', opens InventoryForm prefilled for selected item.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        self.open_edit_form(item)

    def _on_action_delete(self, source_row: int):
        # Called when clicking 'Delete' in 'Actions', asks for confirmation then deletes.
        if source_row < 0 or source_row >= len(self.base_model.items):
            return
        item = self.base_model.items[source_row]
        confirm = QMessageBox.question(
            self, "Delete",
            f"Delete item {item.part_number}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            InventoryItem.delete_by_part_number(item.part_number, self.user)
            self.load_items()
            from ui.signals.model_signals import model_signals
            model_signals.inventory_changed.emit()

    # Table selection helpers: delete/order using currently selected row
    def delete_selected(self, index: Optional[QModelIndex] = None):
        # Delete selected row. If no index is provided, it uses table's current selection.
        if index is None or not index.isValid():
            idx = self.table.currentIndex()
            if not idx.isValid():
                return
            index = idx

        source_row = self.proxy.mapToSource(index).row()
        item = self.base_model.items[source_row]

        confirm = QMessageBox.question(
            self, "Delete",
            f"Delete item {item.part_number}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            InventoryItem.delete_by_part_number(item.part_number, self.user)
            self.load_items()
            from ui.signals.model_signals import model_signals
            model_signals.inventory_changed.emit()

    def order_selected(self, index: Optional[QModelIndex] = None):
        # Start order for selected item; shows warning if nothing is selected.
        if index is None or not index.isValid():
            idx = self.table.currentIndex()
            if not idx.isValid():
                QMessageBox.warning(self, "No Selection", "Please select an inventory item first.")
                return
            index = idx

        source_row = self.proxy.mapToSource(index).row()
        self._on_action_order(source_row)

    # Header right-click: open per-column filter popup
    def _on_header_context_menu(self, pos: QPoint):
        # On right-click, open filter popup for that specific column.

        header = self.table.horizontalHeader()
        logical = header.logicalIndexAt(pos)
        if logical < 0 or logical >= len(self.all_columns):
            return
        col_index = logical
        self.open_column_filter_popup(col_index)

    def _get_current_filtered_items(self, exclude_col: Optional[str] = None) -> List[Any]:
        # Return the list of items that pass all active filters, optionally ignoring
        # a single column's filter (used so that filter popup can see the "raw" values)

        filtered = self.base_model.items
        for col_name, allowed_set in self.active_column_filters.items():
            if exclude_col and col_name == exclude_col:
                continue
            filtered = [
                it for it in filtered
                if ("" if getattr(it, col_name, "") is None else str(getattr(it, col_name, ""))) in allowed_set
            ]
        return filtered

    # Open add/edit forms; create a dialog that blocks until user clicks 'save'/'cancel'. On
    # successful save, dialog notifies page to reload data.
    def open_add_form(self):
        dlg = InventoryForm(self,item=None,on_save=self._after_save)
        dlg.exec()

    def open_edit_form(self, item):
        dlg = InventoryForm(self,item=item,on_save=self._after_save)
        dlg.exec()

    def _after_save(self):
        self.load_items()
        from ui.signals.model_signals import model_signals
        model_signals.inventory_changed.emit()

    def import_from_excel(self):
        from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
        from core.importers.inventory_importer import import_inventory_from_excel
        import openpyxl

        # Ask user for file
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Inventory Spreadsheet", "", "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            # Ask for sheet
            wb = openpyxl.load_workbook(path)
            sheet_names = wb.sheetnames

            sheet_name, ok = QInputDialog.getItem(
                self,
                "Select Sheet",
                "Choose which sheet to import:",
                sheet_names,
                0,
                False
            )
            if not ok:
                wb.close()
                return
            wb.close()

            # Run the core importer
            added, missing = import_inventory_from_excel(path, sheet_name, self.user)

            if missing:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"The file is missing required columns:\n- " + "\n- ".join(missing)
                )
                return

            # Refresh UI
            self.load_items()
            self._update_header_icons()

            from ui.signals.model_signals import model_signals
            model_signals.inventory_changed.emit()

            QMessageBox.information(
                self,
                "Import Complete",
                f"✔ Successfully imported {added} items from sheet: {sheet_name}\n\n"
                "Please review the Category column — it may need manual confirmation."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing:\n{e}"
            )

    # Make sure the "Actions" column is always wide enough to show 3 buttons.
    def _actions_logical_index(self) -> int:
        # Return the index of the 'actions' column in all_columns. If it's missing, return -1.
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
        dlg = InventoryHelpDialog(self)
        dlg.exec()
