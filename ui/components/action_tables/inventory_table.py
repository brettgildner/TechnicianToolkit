from __future__ import annotations
from typing import List, Dict, Any
from PySide6.QtCore import (Qt, QAbstractTableModel, QModelIndex)
from PySide6.QtGui import QBrush, QColor

"""
This module defines the InventoryTableModel, a Qt table model that converts a list of InventoryItem 
objects into a structure suitable for display in a QTableView. It specifies the number of rows and 
columns, provides readable column headers, and returns the appropriate text, alignment, and color 
styling for each cell—including special background and foreground colors for toner-related part 
descriptions and a placeholder text for the Actions column. The model also marks which cells are 
selectable or read-only, and includes a set_items method to refresh the entire table when the 
underlying inventory data changes.

ui.components.action_tables.inventory_table.py index:

class InventoryTableModel(): Converts a list of Inventory objects into a drawable format
 - def __init__(): Initialize items and column metadata.
 - def rowCount(): Number of rows = number of items
 - def columnCount(): Number of columns defined in self.columns
 - def headerData(): Human-readable names for the table headers
 - def flags(): Flags define how cells behave (selectable? editable?)
 - def data(): Cell content returned here
 - def set_items(): Replaces entire dataset and refreshes the table
"""

# Inventory table model: converts a list of Inventory objects into a format that
# QTableView can draw. Every column corresponds to a field like "model", "part number", etc.
class InventoryTableModel(QAbstractTableModel):
    def __init__(self, items: List[Any], all_columns: List[str], column_labels: Dict[str, str]):
        super().__init__()
        # items = list of InventoryItem objects coming from the database
        self.items = items
        # all_columns = list of internal field names (keys used to access item attributes)
        self.all_columns = all_columns
        # column_labels = mapping of internal field name -> human-readable column header
        self.column_labels = column_labels

    def rowCount(self, parent=QModelIndex()) -> int:
        # How many rows to show
        return len(self.items)

    def columnCount(self, parent=QModelIndex()) -> int:
        # How many columns to show
        return len(self.all_columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        # This defines what text appears in the table header row (column names)
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            key = self.all_columns[section]
            return self.column_labels.get(key, key)
        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex):
        # Flags describe what the cell can do (selectable, editable, etc.)
        if not index.isValid():
            return Qt.ItemIsEnabled
        key = self.all_columns[index.column()]

        if key == "actions":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
    # What text to show in each cell (DisplayRole), how to align the text (TextAlignmentRole),
    # whether to change background/foreground colors (BackgroundRole/ForegroundRole)
        if not index.isValid():
            return None

        item = self.items[index.row()]
        key = self.all_columns[index.column()]

        # Display text in the cell
        if role == Qt.DisplayRole:
            if key == "actions":
                return "Order | Edit | Delete"
            val = getattr(item, key, "")
            return "" if val is None else str(val)

        # Text alignment
        if role == Qt.TextAlignmentRole:
            if key == "actions":
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        # Actions column colors
        if role == Qt.ForegroundRole and key == "actions":
            return QBrush(Qt.white)
        if role == Qt.BackgroundRole and key == "actions":
            return QBrush(Qt.darkCyan)

        # Color-coding ot part description background; to use the description text to detect
        # color words like "black", "yellow", "cyan", "magenta" and lightly color the background
        # of the Description column so those items stand out.
        if role == Qt.BackgroundRole and key == "part_description":
            desc = str(getattr(item, "part_description", "")).lower()
            # If the text contains certain color names, use a matching background color.
            if "black" in desc:
                # Dark gray background for "black" items.
                return QBrush(Qt.darkGray)
            elif "yellow" in desc:
                # Light yellow background to stay readable.
                return QBrush(QColor("#fff799"))
            elif "cyan" in desc:
                # Soft cyan background.
                return QBrush(QColor("#b5ffff"))
            elif "magenta" in desc:
                # Soft magenta background.
                return QBrush(QColor("#ffb5ff"))
            # If no color keyword was found, keep the default table background.
            return QBrush(Qt.transparent)

        # Make sure text is always readable over the chosen background colors.
        if role == Qt.ForegroundRole and key == "part_description":
            desc = str(getattr(item, "part_description", "")).lower()

            # On light backgrounds (yellow, cyan, magenta), use black text.
            if any(color in desc for color in ("yellow", "cyan", "magenta")):
                return QBrush(Qt.black)

            # On dark background (for "black"), white text.
            if "black" in desc:
                return QBrush(Qt.white)
            return None
        return None

    def set_items(self, items: List[Any]):
        # When the underlying data list changes, notify Qt to fully refresh the table.
        self.beginResetModel()
        self.items = items
        self.endResetModel()