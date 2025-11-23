from __future__ import annotations
from typing import Dict, Set
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
                               QCheckBox, QScrollArea)

"""
This module provides the UI logic for column-based filtering and visibility control within table 
views. It includes dialogs that let users filter a single column or manage all filters and visible 
columns at once, using checkbox-driven selection interfaces. The functions gather unique values from 
the table’s data, build interactive filter popups, apply or reset filter rules, update header icons, 
and refresh the table display. Overall, this page serves as the user-facing layer that allows dynamic 
filtering and column customization in the application’s data tables.

ui.components.filters.inventory_column_filter_popup.py index:
def open_column_filter_popup(): Show filter options for one column.
 - def select_all(): Check all values.
 - def clear_all(): Uncheck all values.
 - def apply_and_close(): Apply column filter and close dialog.
def open_filter_window(): Full filters & column visibility dialog.
 - def clear_filters_all(): Reset all filters and show all columns.
 - def apply_all(): Apply all filter and visibility changes.
def clear_filters(): Clear all filters and reset table.
"""

def open_column_filter_popup(self, col_index: int):
    # Show available filter values for that column in a tick/untick format.

    col_name = self.all_columns[col_index]
    if col_name not in self.visible_columns:
        # Column is hidden, ignore filter request.
        return

    # Skip actions column– it's not filterable.
    if col_name == "actions":
        return

    filtered_items = self._get_current_filtered_items(exclude_col=col_name)
    unique_values = sorted({
        ("" if getattr(it, col_name, "") is None else str(getattr(it, col_name, "")))
        for it in filtered_items
    })

    dlg = QDialog(self)
    dlg.setWindowTitle(f"Filter: {self.column_labels.get(col_name, col_name)}")
    dlg.setMinimumSize(380, 480)
    v = QVBoxLayout(dlg)
    v.addWidget(QLabel(f"Filter by {self.column_labels.get(col_name, col_name)}"))

    # The scroll area contains one checkbox per unique value for this column.
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    list_layout = QVBoxLayout(w)

    existing = self.active_column_filters.get(col_name)
    # No filter exists yet: all values are pre-selected by default.
    preselected = set(existing) if existing else set(unique_values)

    cb_by_value: Dict[str, QCheckBox] = {}
    for val in unique_values:
        text = val if val else "(blank)"
        cb = QCheckBox(text)
        cb.setChecked(val in preselected)
        list_layout.addWidget(cb)
        cb_by_value[val] = cb

    list_layout.addStretch()
    scroll.setWidget(w)
    v.addWidget(scroll)

    # Footer: Select All / Clear All / Apply
    footer = QHBoxLayout()
    btn_all = QPushButton("Select All")
    btn_none = QPushButton("Clear All")
    btn_apply = QPushButton("Apply")
    for b in (btn_all, btn_none, btn_apply):
        b.setCursor(QCursor(Qt.PointingHandCursor))
    footer.addWidget(btn_all)
    footer.addWidget(btn_none)
    footer.addStretch()
    footer.addWidget(btn_apply)
    v.addLayout(footer)

    def select_all():
        # Mark all possible values as selected.
        for b in cb_by_value.values():
            b.setChecked(True)

    def clear_all():
        # Uncheck all values.
        for b in cb_by_value.values():
            b.setChecked(False)

    def apply_and_close():
        # Build a set of chosen values.
        chosen = {val for val, cb in cb_by_value.items() if cb.isChecked()}
        # Choosing 'none' or 'all' = treated as "no filter" for this column.
        if not chosen or len(chosen) == len(unique_values):
            self.active_column_filters.pop(col_name, None)
        else:
            self.active_column_filters[col_name] = chosen

        # Apply filters and update header labels.
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()
        dlg.accept()

    btn_all.clicked.connect(select_all)
    btn_none.clicked.connect(clear_all)
    btn_apply.clicked.connect(apply_and_close)
    dlg.exec()

# Global filters & columns dialog; filter columns by values, choose column visibility
def open_filter_window(self):
    # Open simple Filters & Columns dialog; columns list checkbox options only,
    # no per-column 'Select All / Clear All' buttons, Global 'Apply' button applies
    # filters and column visibility.

    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget,
        QCheckBox, QPushButton, QFrame, QMessageBox
    )
    from PySide6.QtCore import Qt

    dlg = QDialog(self)
    dlg.setWindowTitle("Filters & Columns")
    dlg.resize(520, 600)
    outer = QVBoxLayout(dlg)
    outer.setSpacing(10)

    # Scroll area for filter checkboxes (one section per column).
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    outer.addWidget(scroll, 1)

    wrap = QWidget()
    wrap_layout = QVBoxLayout(wrap)
    wrap_layout.setSpacing(14)

    self._checks_by_col: dict[str, list[QCheckBox]] = {}

    src_model = self.base_model
    headers = src_model.all_columns
    data_items = src_model.items

    # Build a section for each column (except 'actions').
    for col_name in headers:
        if col_name == "actions":
            continue  # Skip non-filterable column

        # Gather unique values present in this column.
        values = sorted({
            "" if getattr(it, col_name, "") is None else str(getattr(it, col_name, ""))
            for it in data_items
        })

        title = QLabel(self.column_labels.get(col_name, col_name))
        title.setStyleSheet('color:#00ff99; font: bold 13px "Segoe UI";')
        wrap_layout.addWidget(title)

        checks = []
        existing = self.active_column_filters.get(col_name)
        preselected = set(existing) if existing else set(values)

        # Create one checkbox per unique value.
        for v in values:
            cb = QCheckBox(v if v else "(blank)")
            cb.setChecked(v in preselected)
            cb.setStyleSheet("QCheckBox{color:#ddd;}")
            wrap_layout.addWidget(cb)
            checks.append(cb)

        self._checks_by_col[col_name] = checks

        # Visual separator between column sections.
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#333; max-height:1px;")
        wrap_layout.addWidget(sep)

    wrap_layout.addStretch(1)
    scroll.setWidget(wrap)

    # Visible columns section: choose which columns to show/hide.
    col_label = QLabel("Visible Columns")
    col_label.setStyleSheet('color:#00ff99; font: bold 14px "Segoe UI";')
    outer.addWidget(col_label)

    visible_checks: dict[str, QCheckBox] = {}
    for col_name in headers:
        cb = QCheckBox(self.column_labels.get(col_name, col_name))
        cb.setChecked(col_name in self.visible_columns)
        cb.setStyleSheet("QCheckBox{color:#ddd;}")
        outer.addWidget(cb)
        visible_checks[col_name] = cb

    # Footer with buttons: Clear All Filters / Apply / Close
    footer = QHBoxLayout()
    footer.addStretch(1)
    btn_clear_filters = QPushButton("Clear All Filters")
    btn_apply = QPushButton("Apply")
    btn_close = QPushButton("Close")
    for b in (btn_clear_filters, btn_apply, btn_close):
        b.setCursor(QCursor(Qt.PointingHandCursor))
    footer.addWidget(btn_clear_filters)
    footer.addWidget(btn_apply)
    footer.addWidget(btn_close)
    outer.addLayout(footer)

    def clear_filters_all():
    # Clear all filtering rules and make all columns visible again.
        self.active_column_filters.clear()
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()

        # Reset all per-column checkboxes to "checked".
        for checks in self._checks_by_col.values():
            for cb in checks:
                cb.setChecked(True)

        # Make all columns visible again.
        self.visible_columns = list(self.all_columns)
        self._apply_visible_columns()

        # Reset the "Visible Columns" checkboxes too.
        for cb in visible_checks.values():
            cb.setChecked(True)

        dlg.accept()

    def apply_all():
    # Build filter sets/visibility list from checkboxes and apply to table.

        new_filters: Dict[str, Set[str]] = {}

        # Build filters from the scrollable column sections.
        for col, cbs in self._checks_by_col.items():
            selected = {cb.text() if cb.text() != "(blank)" else "" for cb in cbs if cb.isChecked()}
            all_vals = {cb.text() if cb.text() != "(blank)" else "" for cb in cbs}
            # Only treat as a filter if not all (or none) are selected.
            if selected and selected != all_vals:
                new_filters[col] = selected

        self.active_column_filters = new_filters
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()

        # Compute which columns should be visible.
        new_visible = [k for k, cb in visible_checks.items() if cb.isChecked()]
        if not new_visible:
            QMessageBox.warning(self, "No Columns Visible", "At least one column must remain visible.")
            return
        self.visible_columns = new_visible
        self._apply_visible_columns()
        dlg.accept()

    btn_clear_filters.clicked.connect(clear_filters_all)
    btn_apply.clicked.connect(apply_all)
    btn_close.clicked.connect(dlg.reject)

    dlg.exec()

# Clear filters button (toolbar); quick 'reset all' button, refreshes table completely.
def clear_filters(self):
    # Clear all active filters and show all columns again. Reset filter rules.
    self.active_column_filters.clear()
    self.proxy.set_filters(self.active_column_filters)
    self._update_header_icons()

    # Show all columns again.
    self.visible_columns = list(self.all_columns)
    self._apply_visible_columns()

    # Force a full refresh of the proxy and table display.
    self.proxy.invalidate()
    self.table.reset()
    self.table.viewport().update()