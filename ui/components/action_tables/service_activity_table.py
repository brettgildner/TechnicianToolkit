from __future__ import annotations
from typing import List, Dict
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QBrush, QColor
from core.models.service_activity_model import ServiceActivity

"""
This module defines the ServiceActivityTableModel, a Qt table model that converts a list of 
ServiceActivity objects into a structure suitable for display and interaction within a QTableView. 
It provides the row and column layout, readable column headers, and the text, alignment, and coloring 
shown in each cell—including a placeholder for the Actions column handled by a delegate and editable 
support for the part_replaced field. The model manages selection and editability rules, updates 
underlying objects when edits occur, and can refresh the entire dataset through set_items, serving as 
the core data source for the Service Activity table UI.

ui.components.action_tables.service_activity_table.py index: 

class ServiceActivityTableModel(): Converts a list of Service Activity objects into a drawable format
 - def __init__(): Initialize activities and column metadata.
 - def rowCount(): Number of rows = number of items
 - def columnCount(): Number of columns defined in self.columns
 - def headerData(): Human-readable names for the table headers
 - def flags(): Flags define how cells behave (selectable? editable?)
 - def data(): Cell content returned here
 - def set_items(): Replaces entire dataset and refreshes the table
"""

# Table model that supplies data and formatting for the service activity table.
class ServiceActivityTableModel(QAbstractTableModel):
    # Defines the table’s rows, columns, and display behavior without handling filters or buttons.
    def __init__(
        self,
        items: List[ServiceActivity],
        all_columns: List[str],
        column_labels: Dict[str, str]
    ):
        super().__init__()
        # List of ServiceActivity objects to show in the table.
        self.items = items
        # List of column keys (attributes on ServiceActivity, e.g., "customer").
        self.all_columns = all_columns
        # Human-readable labels for each column key.
        self.column_labels = column_labels

    # --- Required overrides so Qt knows the table's structure ----------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # How many rows are in the table? One row per ServiceActivity item.
        return len(self.items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # How many columns? One column per entry in all_columns.
        return len(self.all_columns)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole
    ):
        # Returns the display text for column headers.
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            key = self.all_columns[section]
            # Return human-readable label, refer to the raw key if missing.
            return self.column_labels.get(key, key)
        return super().headerData(section, orientation, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        key = self.all_columns[index.column()]

        if key == "actions":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if key == "part_replaced":
            # Defines which cells are editable or selectable.
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        # Provides the cell's display text, alignment, and optional coloring.
        if not index.isValid():
            return None

        # Which ServiceActivity object is this row representing?
        item = self.items[index.row()]
        # Which field (column) is being displayed?
        key = self.all_columns[index.column()]

        # Text to display in the cell
        if role == Qt.DisplayRole:
            if key == "actions":
                # Placeholder text-- the visual "buttons" are drawn by the delegate, but the table still
                # expects some string.
                return "Edit | Delete"

            # For any other column, read the attribute from the ServiceActivity object.
            val = getattr(item, key, "")
            return "" if val is None else str(val)

        # Text alignment
        if role == Qt.TextAlignmentRole:
            if key == "actions":
                # Center-align the "Edit / Delete" text in the actions column so the buttons are centered.
                return Qt.AlignCenter
            # All other cells: left-aligned, vertically centered.
            return Qt.AlignLeft | Qt.AlignVCenter

        # Colors for the Actions column
        if role == Qt.ForegroundRole and key == "actions":
            # White placeholder text.
            return QBrush(Qt.white)

        if role == Qt.BackgroundRole and key == "actions":
            # Slightly tinted background to visually separate this column.
            return QBrush(QColor("#204050"))

        # For all other cases, do nothing special.
        return None

    # Helper to reset all data at once
    def set_items(self, items: List[ServiceActivity]):
        # Replaces all items and refreshes the table.
        self.beginResetModel()
        self.items = items
        self.endResetModel()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        key = self.all_columns[col]

        # Update the underlying ServiceActivity instance
        setattr(self.items[row], key, value)

        # Notify Qt that data changed
        self.dataChanged.emit(index, index, [Qt.EditRole])

        return True