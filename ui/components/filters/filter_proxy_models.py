from __future__ import annotations
from typing import Dict, Set, List, Any
from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt
from ui.components.action_tables.inventory_table import InventoryTableModel
from ui.components.action_tables.service_activity_table import ServiceActivityTableModel

"""
This module defines a collection of proxy filter models that sit between table data and the UI, 
controlling which rows are visible based on user-selected criteria. It provides several specialized 
filtering classes—some using column-specific allow-lists, others using substring or text-matching 
rules—to support pages like Inventory, Parts, Service Activity, and Mileage. Each proxy evaluates 
rows in the underlying data model and hides those that don’t meet the active filter conditions, 
enabling flexible, dynamic table filtering throughout the application.

ui.components.filters.filter_proxy_models.py index:
class ColumnFilterProxy(): Column-based allow-list filter proxy.
 - def __init__(): Initialize filter proxy.
 - def set_filters(): Replace filters and refresh.
 - def filterAcceptsRow(): Check if row matches filters.
class ServiceActivityFilterProxy(): Filter proxy for Service Activity rows.
 - def __init__(): Initialize Service Activity filter.
 - def set_filters(): Replace filters and refresh.
 - def filterAcceptsRow(): Test row against filters.
 - def flags(): Return source model item flags.
class InventoryFilterProxy(): Filter proxy for Inventory rows.
 - def __init__(): Initialize Inventory filter.
 - def set_filters(): Replace filters and refresh.
 - def filterAcceptsRow(): Test row against filters.
class MileageFilterProxy(): Text-based substring filtering proxy.
 - def __init__(): Initialize text filter proxy.
 - def set_text_filter(): Set substring filter for column.
 - def clear_all_filters(): Remove all text filters.
 - def filterAcceptsRow(): Test row against filters.
class PartsFilterProxy(): Case-insensitive substring filter per column.
 - def __init__(): Initialize parts filter.
 - def set_filters(): Replace filters and refresh.
 - def filterAcceptsRow(): Test row against filters.
"""

class ColumnFilterProxy(QSortFilterProxyModel):
    # A generic allow-list–based filtering proxy used by pages such as Inventory, Parts
    # Orders, and Service Activity. Only rows whose item.category AND item.model match the
    # allowed sets remain visible in the table.

    def __init__(self, filters: Dict[str, Set[str]], columns: List[str], parent=None):
        super().__init__(parent)
        self.filters = filters
        self.columns = columns

    def set_filters(self, filters: Dict[str, Set[str]]):
        # Replace all existing filters with a new filter dictionary, then force Qt to re-run
        # filterAcceptsRow() for every row. invalidateFilter() = "Something changed,
        # re-evaluate all row visibility."
        self.filters = filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Qt calls this once per row each time filtering is reapplied. Returns 'True' (keep
        # rows visible) or 'False' (hide row). The logic walks through each filter entry and
        # checks whether the corresponding attribute on the row object is inside the allow-list.

        src = self.sourceModel()
        # If the model doesn't appear to have row objects, don't filter.
        if not hasattr(src, "items"):
            return True
        items: List[Any] = getattr(src, "items", [])
        if source_row < 0 or source_row >= len(items):
            return True

        # Extract the Python object representing this row.
        item = items[source_row]

        #  Evaluate filter rules, a row must pass every active filter.
        for col_name, allowed in self.filters.items():

            # If set empty = no filtering on this column
            if not allowed:
                continue

            # If the column key is not recognized, skip it
            if col_name not in self.columns:
                continue

            # Read the item attribute using getattr
            val = getattr(item, col_name, "")

            # Convert None to "", and everything else to a string
            sval = "" if val is None else str(val)

            # If the cell value is NOT in the allow-list, the row fails
            if sval not in allowed:
                return False

        # If no filter rejected the row, the row is accepted
        return True

class ServiceActivityFilterProxy(QSortFilterProxyModel):
# Filter proxy model; this layer sits between the raw data and the visible table, it hides
# rows that do not match the active filters.
    def __init__(self, filters: Dict[str, Set[str]], all_columns: List[str]):
        super().__init__()
        self.filters = filters
        self.all_columns = all_columns

    def set_filters(self, filters: Dict[str, Set[str]]):
        # Replaces the active filters and triggers row re-evaluation.
        self.filters = filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Determines whether a row matches the active per-column filter sets.
        src: ServiceActivityTableModel = self.sourceModel()
        if not isinstance(src, ServiceActivityTableModel):
            return True
        item = src.items[source_row]

        # Check each active filter rule.
        for col_name, allowed in self.filters.items():
            if not allowed:
                continue

            val = getattr(item, col_name, "")
            sval = "" if val is None else str(val)
            if sval not in allowed:
                # One filter fails = hide row.
                return False

        # If all filters passed, show the row.
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        # Map the proxy index to the source index
        src_index = self.mapToSource(index)

        # Return the flags from the source model
        return self.sourceModel().flags(src_index)

class InventoryFilterProxy(QSortFilterProxyModel):
# Filter proxy model; this layer sits between the raw data and the visible table, it hides
# rows that do not match the active filters.
    def __init__(self, filters: Dict[str, Set[str]], all_columns: List[str]):
        super().__init__()
        self.filters = filters
        self.all_columns = all_columns

    def set_filters(self, filters: Dict[str, Set[str]]):
        # Replace filters and trigger a re-check of all rows.
        self.filters = filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # For each row coming from the base model, decide "keep" (True) or "hide" (False)
        src: InventoryTableModel = self.sourceModel()  # type: ignore
        if not isinstance(src, InventoryTableModel):
            return True
        item = src.items[source_row]

        # Check every active filter; if any filter does not match, hide the row.
        for col_name, allowed in self.filters.items():
            if not allowed:
                # If the set of allowed values is empty, skip that filter.
                continue
            val = getattr(item, col_name, "")
            sval = "" if val is None else str(val)
            if sval not in allowed:
                return False
        return True

class MileageFilterProxy(ColumnFilterProxy):
# Filter proxy model; this layer sits between the raw data and the visible table, it hides
# rows that do not match the active filters.
    def __init__(self, columns: List[str], parent=None):
        super().__init__(filters={}, columns=columns, parent=parent)
        self._text_filters: Dict[str, str] = {}

    def set_text_filter(self, column_key: str, text: str):
        # Sets or clears a substring filter for the chosen column.
        text = (text or "").strip().lower()

        if not text:
            # If filter is blank, remove it
            self._text_filters.pop(column_key, None)
        else:
            # Store new substring filter
            self._text_filters[column_key] = text

        # Tell Qt to re-check each row
        self.invalidateFilter()

    def clear_all_filters(self):
        # Remove every filter and refresh table.
        self._text_filters.clear()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Determines whether a row passes all active filters.
        src = self.sourceModel()

        # Must use get_item() from the base model
        if not hasattr(src, "get_item"):
            return True

        item = src.get_item(source_row)
        if item is None:
            return True

        # Check each filter
        for col_key, needle in self._text_filters.items():
            val = getattr(item, col_key, "")
            sval = "" if val is None else str(val).lower()

            if needle not in sval:
                # If any filter doesn't match, hide row
                return False

        return True

class PartsFilterProxy(QSortFilterProxyModel):
# Filter proxy that applies case-insensitive substring filters.
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns
        self.column_filters: Dict[int, str] = {}

    def set_filters(self, filters: Dict[int, str]):
        # Receives a dictionary of substring filters for specific columns.
        self.column_filters = filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Determines whether a row matches all active substring filters.
        if not self.column_filters:
            return True

        src = self.sourceModel()
        if src is None:
            return True

        for col_idx, text in self.column_filters.items():
            if not text:
                continue

            idx = src.index(source_row, col_idx, source_parent)
            val = src.data(idx, Qt.DisplayRole)
            sval = ("" if val is None else str(val)).lower()

            if text not in sval:
                return False

        return True