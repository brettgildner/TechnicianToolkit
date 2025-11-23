from __future__ import annotations
from typing import Any, List, Dict
from PySide6.QtCore import (QAbstractTableModel, QModelIndex, Qt)
from PySide6.QtGui import QColor

"""
This module defines the BaseTableModel, a reusable, theme-friendly Qt table model designed to support 
any list-based dataset. It handles the essential responsibilities of a QAbstractTableModel: reporting 
row and column counts, returning cell text and alignment, drawing dark-theme alternating row 
backgrounds, and providing optional color-coding (such as toner-color highlights for part_description). 
The model also supplies utility methods for safely accessing items, replacing all data, customizing 
how values are extracted via get_value, and supporting in-table editing through setData. It serves as 
a generic foundation that more specialized table models in the application can extend or use directly.

ui.components.base_tables.base_table_model.py index:

class BaseTableModel(): Generic reusable table model.
 - def __init__(): Store items and column definitions.
 - def rowCount(): Number of rows = number of items
 - def columnCount(): Number of columns defined in self.columns
 - def data(): Cell content returned here
 - def headerData(): Human-readable names for the table headers
 - def get_value(): Extracts a column's value from a row object
 - def set_items(): Replaces entire dataset and refreshes the table
 - def get_item(): Safe accessor for a single row's object
 - def items(): Returns the raw list of row objects
 - def setData(): Handles editing of table cells
    """

class BaseTableModel(QAbstractTableModel):
    # Reusable, generic table model for dark-themed apps. Intended use: 'items' is a list of
    # arbitrary Python objects (ORM rows, objects, dict-like, etc), 'columns' is a list of
    # attribute names to extract from each item, 'column_labels' maps those attribute names
    # to readable text labels. This class handles returning row/column counts, extracting
    # values via getattr(), display formatting, dark alternating row colors, auto-labeling
    # of headers, optional color highlighting for "part_description" (InventoryPage). It is
    # flexible enough to be subclasses, extended, or reused as-is.

    def __init__(self, items: List[Any], columns: List[str], column_labels: Dict[str, str]):
        super().__init__()
        self._items: List[Any] = items or []
        self.columns = columns
        self.column_labels = column_labels or {c: c for c in columns}

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # Returns total number of table rows
        return len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # Returns number of visible columns
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        # Core method, handles how cells appear; handles: DisplayRole (text inside cell),
        # TextAlignmentRole (left/center/etc), BackgroundRole (alternate shading + optional
        # color highlight). Very generic by design, subclasses can override get_value() to
        # implement special column logic per-row.

        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # Current item object
        item = self._items[row]

        # Attribute name for the column
        key = self.columns[col]

        # --------------------------- DISPLAY TEXT ---------------------------
        if role == Qt.DisplayRole:
            # Default behavior:
            #     Call get_value() which by default uses getattr()
            return str(self.get_value(item, key))

        # ------------------------- TEXT ALIGNMENT --------------------------
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        # --------------------- BACKGROUND COLORING -------------------------
        if role == Qt.BackgroundRole:

            # Standard alternating row colors (dark theme)
            base_color = QColor("#2f2f2f") if row % 2 == 0 else QColor("#3a3a3a")

            # Only the "part_description" column gets extra highlight options.
            # If this column does not exist, return the base color.
            try:
                desc_col = self.columns.index("part_description")
            except ValueError:
                return base_color

            # If this is NOT the description column, return the default background.
            if col != desc_col:
                return base_color

            # Retrieve description text for color-coding logic
            desc = str(self.get_value(item, "part_description")).lower()

            # Apply special theme-based color overlays based on keywords
            if "black" in desc:
                return QColor("#5a5a5a")      # dark-gray highlight
            elif "yellow" in desc:
                return QColor("#fff799")      # pale yellow
            elif "cyan" in desc:
                return QColor("#b5ffff")      # soft cyan
            elif "magenta" in desc:
                return QColor("#ffb5ff")      # light magenta

            # If no keyword matches, return the normal alternating base color
            return base_color

        # For any other role, return nothing
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        # Controls the table's header labels. Horizontal headers: show readable column names.
        # Vertical headers: show 1-based row numbers.

        if role != Qt.DisplayRole:
            return None

        # Horizontal titles (column headers)
        if orientation == Qt.Horizontal:
            key = self.columns[section]
            return self.column_labels.get(key, key)

        # Vertical left-side labels (row numbers)
        return section + 1

    # ----------------------------------------------------------------------
    # PUBLIC UTILITY METHODS
    # ----------------------------------------------------------------------

    def get_value(self, item: Any, column_key: str):
        # Extracts a column's value from a row object. Default behavior: getattr(item,
        # column_key, "") or "". This method is intentionally overrideable. Subclasses
        # can convert, format, combine fields, etc.
        return getattr(item, column_key, "") or ""

    def set_items(self, items: List[Any]):
        # Replace the model's rows entirely. This triggers a full model reset (efficient
        # inside Qt), causing the table to redraw itself automatically.
        self.beginResetModel()
        self._items = items or []
        self.endResetModel()

    def get_item(self, row: int) -> Any | None:
        # Safe accessor for a single row's object. Returns None if the row is out of bounds.
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def items(self) -> List[Any]:
        # Returns the raw list of row objects.
        return self._items

    # ----------------------------------------------------------------------
    # ENABLE EDITING SUPPORT
    # ----------------------------------------------------------------------
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole):
        # Handles editing of table cells. Required for delegates (like PartComboDelegate) to
        # work. Steps: 1. Write the value into the underlying Python object 2. Emit dataChanged
        # so Qt knows something changed 3. Return True (Qt requires this or it discards the edit)
        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        item = self.get_item(row)
        if item is None:
            print("DEBUG: setData aborted — row item is None")
            return False

        key = self.columns[col]

        try:
            # Update the Python object attribute
            setattr(item, key, value)
            print(f"DEBUG: setData wrote {key} = {value} into row {row}")
        except Exception as e:
            print("DEBUG: setData setattr failed:", e)
            return False

        # Notifies views & proxy that data changed
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        print("DEBUG: setData emitted dataChanged")

        return True
