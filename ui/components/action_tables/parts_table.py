from typing import List, Dict
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor
from core.models.parts_model import PartsOrder

"""
This module defines the PartsTableModel, a Qt table model that adapts a list of PartsOrder objects 
into a format that a QTableView can display. It specifies how many rows and columns the table contains, 
provides readable header labels, and supplies the appropriate display values—including a placeholder 
for the Actions column that is rendered by a delegate. The model controls cell selection behavior, 
aligns numeric fields for readability, colors the Actions column text, and includes a set_items method 
to refresh the table whenever the underlying parts data changes.

ui.components.action_tables.parts_table.py index: 

class PartsTableModel(): Converts a list of Parts objects into a drawable format
 - def __init__(): Store items, columns, labels.
 - def rowCount(): Number of rows = number of items
 - def columnCount(): Number of columns defined in self.columns
 - def headerData(): Human-readable names for the table headers
 - def flags(): Flags define how cells behave (selectable? editable?)
 - def data(): Cell content returned here
 - def set_items(): Replaces entire dataset and refreshes the table

"""

# Table model for supplying row and column data to the table.
class PartsTableModel(QAbstractTableModel):
    def __init__(self, items: List[PartsOrder], columns: List[str], column_labels: Dict[str, str]):
        super().__init__()
        self.items = items
        self.columns = columns
        self.column_labels = column_labels

    def rowCount(self, parent=QModelIndex()) -> int:
        # Returns the number of rows in the table.
        return len(self.items)

    def columnCount(self, parent=QModelIndex()) -> int:
        # Returns the number of columns.
        return len(self.columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        # Provides the text shown in the table header.
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            key = self.columns[section]
            return self.column_labels.get(key, key)
        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex):
        # Defines selection behavior and disables in-table editing.
        if not index.isValid():
            return Qt.ItemIsEnabled

        key = self.columns[index.column()]
        if key == "actions":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        # Returns the display value for each cell, using a placeholder for actions.
        if not index.isValid():
            return None

        item = self.items[index.row()]
        key = self.columns[index.column()]

        # What text appears in each cell
        if role == Qt.DisplayRole:
            if key == "actions":
                return "Edit | Delete"
            val = getattr(item, key, "")
            return "" if val is None else str(val)

        # Center numeric-like cells
        if role == Qt.TextAlignmentRole:
            if key in ("id", "quantity"):
                return Qt.AlignCenter
            if key == "actions":
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        # Make text white for actions column
        if role == Qt.ForegroundRole and key == "actions":
            return QColor("#ffffff")

        return None

    def set_items(self, items: List[PartsOrder]):
        # Replaces the internal data and refreshes the table.
        self.beginResetModel()
        self.items = items
        self.endResetModel()