from __future__ import annotations
from typing import List, Dict
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from core.models.equipment_model import EquipmentInfo

"""
This module defines the EquipmentInfoTableModel, a Qt table model that transforms a list of 
EquipmentInfo objects into a structure that a QTableView can display. It specifies how many rows and 
columns the table has, provides readable header labels, determines cell behaviors through item flags, 
and supplies the actual text shown in each cell—including a placeholder for the actions column handled 
by a delegate. The model also supports refreshing its entire dataset through set_items, ensuring the 
Equipment Info table updates cleanly whenever new information is loaded.

ui.components.action_tables.equipment_table.py index:

class EquipmentInfoTableModel(): Converts a list of EquipmentInfo objects into a drawable format
 - def __init__(): Store items, columns, labels.
 - def rowCount(): Number of rows = number of items
 - def columnCount(): Number of columns defined in self.columns
 - def headerData(): Human-readable names for the table headers
 - def flags(): Flags define how cells behave (selectable? editable?)
 - def data(): Cell content returned here
 - def set_items(): Replaces entire dataset and refreshes the table
"""

# Equipment Info table model: converts a list of EquipmentInfo objects into a format that
# QTableView can draw. Every column corresponds to a field like "area", "customer",
# "serial number", etc.
class EquipmentInfoTableModel(QAbstractTableModel):
    def __init__(self, items: List[EquipmentInfo], columns: List[str], column_labels: Dict[str, str]):
        super().__init__()
        self.items = items
        self.columns = columns
        self.column_labels = column_labels

    # Number of rows = number of items
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.items)

    # Number of columns defined in self.columns
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.columns)

    # Human-readable names for the table headers
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            key = self.columns[section]
            return self.column_labels.get(key, key)
        return super().headerData(section, orientation, role)

    # Flags define how cells behave (selectable? editable?)
    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled
        key = self.columns[index.column()]
        # The "actions" column is not editable — delegate handles it.
        if key == "actions":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Cell content returned here
    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        key = self.columns[index.column()]

        # What shows inside cells
        if role == Qt.DisplayRole:
            # Actions column only shows placeholder text
            if key == "actions":
                return "Edit | Delete"
            val = getattr(item, key, "")
            return "" if val is None else str(val)

        # Align actions column centered; others left-aligned
        if role == Qt.TextAlignmentRole:
            if key == "actions":
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    # Replaces entire dataset and refreshes the table
    def set_items(self, items: List[EquipmentInfo]):
        self.beginResetModel()
        self.items = items
        self.endResetModel()