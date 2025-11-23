from __future__ import annotations
from typing import List, Dict
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QLabel, QPushButton, QDialog, QVBoxLayout as QVLayout, QHBoxLayout as QHLayout,
                               QLineEdit, QFormLayout)

"""
This module defines the PartsFilterDialog-- a header-like filter window that allows users to enter
either an ID, Part Number, Model, Description, or Quantity unique to individual orders that may need
to be searched.
"""

# Filter dialog for editing column-based substring filters.
class PartsFilterDialog(QDialog):
    def __init__(self, parent, columns: List[str], labels: Dict[str, str], current_filters: Dict[int, str]):
        super().__init__(parent)
        self.setWindowTitle("Filter Parts Orders")
        self.setMinimumSize(420, 260)

        self.columns = columns
        self.labels = labels
        self.current_filters = current_filters
        self._edits: Dict[int, QLineEdit] = {}

        layout = QVLayout(self)

        info = QLabel(
            "Enter text to filter rows (case-insensitive). "
            "If a field is empty, that column is not filtered."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        layout.addLayout(form)

        # Build filter rows
        for col_idx, key in enumerate(self.columns):
            if key == "actions" or key == "user":
                continue

            label = labels.get(key, key)
            edit = QLineEdit()
            edit.setPlaceholderText("Contains...")
            existing = self.current_filters.get(col_idx, "")
            edit.setText(existing)

            form.addRow(label + ":", edit)
            self._edits[col_idx] = edit

        # Buttons
        btn_row = QHLayout()
        btn_clear = QPushButton("Clear All")
        btn_ok = QPushButton("Apply")
        btn_cancel = QPushButton("Cancel")

        for b in (btn_clear, btn_ok, btn_cancel):
            b.setCursor(QCursor(Qt.PointingHandCursor))

        btn_row.addStretch()
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        btn_clear.clicked.connect(self._clear)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def _clear(self):
        # Clears all text filter fields.
        for e in self._edits.values():
            e.clear()

    def get_filters(self) -> Dict[int, str]:
        # Returns a dictionary of filters entered in the dialog.
        results: Dict[int, str] = {}
        for col_idx, edit in self._edits.items():
            text = (edit.text() or "").strip().lower()
            if text:
                results[col_idx] = text
        return results