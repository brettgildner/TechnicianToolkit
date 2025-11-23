from __future__ import annotations
from typing import List, Dict, Set
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton,
                               QMessageBox, QDialog, QVBoxLayout as QVLayout, QScrollArea, QCheckBox,
                               QFrame, QHBoxLayout as QHLayout)

"""
This page provides the UI logic for filtering and customizing the display of a data table. It includes 
popup dialogs that let users filter individual columns, apply global filters across all columns, and 
control which columns are visible. It manages collecting unique values, generating checkbox-based 
selection lists, updating filter states, refreshing the table, and ensuring users can quickly show, 
hide, or reset filters and columns.

ui.components.filters.equipment_column_filter_popup.py index:
def open_column_filter_popup(): Show filter options for one column.
 - def select_all(): Check all filter options.
 - def clear_all(): Uncheck all filter options.
 - def apply_and_close(): Apply column filter and close popup.
def open_filter_window(): Open full-table filter/column settings.
 - def clear_filters_all(): Reset all filters and show all columns.
 - def apply_all(): Apply all filters and column visibility changes.
def clear_filters(): Completely remove all filters and reset column visibility.
"""

def open_column_filter_popup(self, col_index: int):
# Show filters for one column
    col_name = self.all_columns[col_index]

    # Skip non-visible or "actions" column
    if col_name not in self.visible_columns:
        return
    if col_name == "actions":
        return

    filtered_items = self._get_current_filtered_items(exclude_col=col_name)

    # Unique values in this column
    unique_values = sorted({
        ("" if getattr(it, col_name, "") is None else str(getattr(it, col_name, "")))
        for it in filtered_items
    })

    dlg = QDialog(self)
    dlg.setWindowTitle(f"Filter: {self.column_labels.get(col_name, col_name)}")
    dlg.setMinimumSize(380, 480)
    v = QVLayout(dlg)
    v.addWidget(QLabel(f"Filter by {self.column_labels.get(col_name, col_name)}"))

    # Scroll list of checkboxes
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    w = QWidget()
    list_layout = QVLayout(w)

    existing = self.active_column_filters.get(col_name)
    preselected = set(existing) if existing else set(unique_values)

    cb_by_value: Dict[str, QCheckBox] = {}

    # Create a checkbox for each possible value
    for val in unique_values:
        text = val if val else "(blank)"
        cb = QCheckBox(text)
        cb.setChecked(val in preselected)
        list_layout.addWidget(cb)
        cb_by_value[val] = cb

    list_layout.addStretch()
    scroll.setWidget(w)
    v.addWidget(scroll)

    # Footer buttons: Select All, Clear All, Apply
    footer = QHLayout()
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
    # Check all filter options.
        for b in cb_by_value.values():
            b.setChecked(True)

    def clear_all():
    # Uncheck all filter options.
        for b in cb_by_value.values():
            b.setChecked(False)

    def apply_and_close():
    # Apply column filter and close popup.
        chosen = {val for val, cb in cb_by_value.items() if cb.isChecked()}
        if not chosen or len(chosen) == len(unique_values):
            self.active_column_filters.pop(col_name, None)
        else:
            self.active_column_filters[col_name] = chosen

        # Update filter + header icons
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()
        dlg.accept()

    btn_all.clicked.connect(select_all)
    btn_none.clicked.connect(clear_all)
    btn_apply.clicked.connect(apply_and_close)

    dlg.exec()

# Global filter window (filters all columns at once)
def open_filter_window(self):
# Opens full filter panel for users to choose visible columns/select values to
# apply per column. Mirrors Inventory page functionality.
    dlg = QDialog(self)
    dlg.setWindowTitle("Filters & Columns")
    dlg.resize(520, 600)
    outer = QVLayout(dlg)
    outer.setSpacing(10)

    # Scrollable area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    outer.addWidget(scroll, 1)

    wrap = QWidget()
    wrap_layout = QVLayout(wrap)
    wrap_layout.setSpacing(14)

    # Mapping of column > list of checkboxes
    self._checks_by_col: Dict[str, List[QCheckBox]] = {}

    src_model = self.base_model
    headers = src_model.columns
    data_items = src_model.items

    # Create filter options for each column
    for col_name in headers:
        if col_name == "actions":
            continue

        # Get unique possible values
        values = sorted({
            "" if getattr(it, col_name, "") is None else str(getattr(it, col_name, ""))
            for it in data_items
        })

        title = QLabel(self.column_labels.get(col_name, col_name))
        title.setStyleSheet('color:#00ff99; font: bold 13px "Segoe UI";')
        wrap_layout.addWidget(title)

        checks: List[QCheckBox] = []
        existing = self.active_column_filters.get(col_name)
        preselected = set(existing) if existing else set(values)

        # Checkbox for each value
        for v in values:
            cb = QCheckBox(v if v else "(blank)")
            cb.setChecked(v in preselected)
            cb.setStyleSheet("QCheckBox{color:#ddd;}")
            wrap_layout.addWidget(cb)
            checks.append(cb)

        self._checks_by_col[col_name] = checks

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#333; max-height:1px;")
        wrap_layout.addWidget(sep)

    wrap_layout.addStretch(1)
    scroll.setWidget(wrap)

    # Column visibility section
    col_label = QLabel("Visible Columns")
    col_label.setStyleSheet('color:#00ff99; font: bold 14px "Segoe UI";')
    outer.addWidget(col_label)

    visible_checks: Dict[str, QCheckBox] = {}
    for col_name in headers:
        cb = QCheckBox(self.column_labels.get(col_name, col_name))
        cb.setChecked(col_name in self.visible_columns)
        cb.setStyleSheet("QCheckBox{color:#ddd;}")
        outer.addWidget(cb)
        visible_checks[col_name] = cb

    # Footer buttons
    footer = QHLayout()
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
    # Reset filters completely
        self.active_column_filters.clear()
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()

        # Reset checkboxes
        for checks in self._checks_by_col.values():
            for cb in checks:
                cb.setChecked(True)

        # Reset column visibility
        self.visible_columns = list(self.all_columns)
        self._apply_visible_columns()
        for cb in visible_checks.values():
            cb.setChecked(True)

        dlg.accept()

    def apply_all():
    # Gather new filter selections
        new_filters: Dict[str, Set[str]] = {}

        for col, cbs in self._checks_by_col.items():
            selected = {cb.text() if cb.text() != "(blank)" else "" for cb in cbs if cb.isChecked()}
            all_vals = {cb.text() if cb.text() != "(blank)" else "" for cb in cbs}

            # Only store filter if user unselected something
            if selected and selected != all_vals:
                new_filters[col] = selected

        # Update filters + header icons
        self.active_column_filters = new_filters
        self.proxy.set_filters(self.active_column_filters)
        self._update_header_icons()

        # Apply visible columns
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

# Top-bar clear filters button
def clear_filters(self):
# Completely remove all filters and reset column visibility.
    self.active_column_filters.clear()
    self.proxy.set_filters(self.active_column_filters)
    self._update_header_icons()

    self.visible_columns = list(self.all_columns)
    self._apply_visible_columns()

    # Force full table redraw
    self.proxy.invalidate()
    self.table.reset()
    self.table.viewport().update()