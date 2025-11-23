from __future__ import annotations
from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtWidgets import (QDialog, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
                               QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QScrollArea,
                               QDateEdit, QTimeEdit, QMessageBox, QFrame, QSpacerItem, QSizePolicy)

"""
This page defines a reusable, styled dialog framework for all form-based windows in the application, 
such as inventory, equipment, mileage, and parts forms. It provides a dark-themed, standardized layout 
with a title, separators, an optional scrollable form area, and Save/Cancel buttons. The BaseDialogForm 
class includes helper methods for adding form fields (text, combo boxes, dates, times, separators), 
retrieving and setting their values, and handling save events. Overall, it serves as the foundation 
for building consistent, structured input forms across the app.

ui.forms.base_dialog_form.py index: 
def hline(): Create horizontal separator.
class BaseDialogForm: Reusable styled form dialog.
 - def __init__(): Initialize dialog layout and styling.
 - def add_line_edit(): Add single-line text field.
 - def add_text_edit(): Add multi-line text field.
 - def add_combo(): Add dropdown field.
 - def add_date(): Add date picker.
 - def add_time(): Add time picker.
 - def add_separator(): Insert labeled section divider.
 - def _get(): Retrieve field value.
 - def _set(): Set field value.
 - def _on_save_clicked(): Handle save button click.
 - def on_save_clicked(): Form save logic (override).
"""

DIALOG_STYLE = """
QDialog {
    background-color: #1f1f1f;
}
QLabel {
    color: #ffffff;
    font: 13px "Segoe UI";
}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
    background-color: #2a2a2a;
    color: #ffffff;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 6px;
}
QPushButton {
    background-color: #0077cc;
    color: #ffffff;
    border-radius: 6px;
    padding: 8px 12px;
}
QPushButton:hover {
    background-color: #0099ff;
}
QPushButton.danger {
    background-color: #8b0000;
}
QPushButton.danger:hover {
    background-color: #a00000;
}
QFrame.line {
    background: #333;
}
"""
# Any dialog that calls setStyleSheet(DIALOG_STYLE) will use these settings.

def hline() -> QFrame:
# Create a thin horizontal line separator.
    line = QFrame()
    line.setObjectName("line")
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet("QFrame#line { background:#333; max-height:1px; }")
    return line

class BaseDialogForm(QDialog):
# Reusable modal form with title label, optional scroll area for tall forms, 'save'/'cancel'
# buttons, and helper methods to add standard fields.

    def __init__(self, parent: Optional[QWidget] = None, *, title: str,
                 width: int = 640, height: int = 540, use_scroll: bool = False):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setWindowModality(Qt.ApplicationModal)
        self.setStyleSheet(DIALOG_STYLE)
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(18, 18, 18, 18)
        self._root_layout.setSpacing(12)

        # ----- Title section -----
        ttl = QLabel(title)
        ttl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        ttl.setStyleSheet('font: bold 20px "Segoe UI"; color: #00e69a;')
        self._root_layout.addWidget(ttl)
        self._root_layout.addWidget(hline())

        # ----- Content container (the main form area) -----
        self._content_widget = QWidget()
        self._form_layout = QFormLayout(self._content_widget)

        # Adjust layout behavior:
        self._form_layout.setLabelAlignment(Qt.AlignRight)
        self._form_layout.setFormAlignment(Qt.AlignTop)
        self._form_layout.setHorizontalSpacing(16)
        self._form_layout.setVerticalSpacing(10)

        if use_scroll:
            # Wrap the content widget in a scroll area for very long forms
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(self._content_widget)
            self._root_layout.addWidget(scroll, 1)
        else:
            # For shorter forms, just add the content widget directly
            self._root_layout.addWidget(self._content_widget, 1)

        # Another separator line before the footer (buttons)
        self._root_layout.addWidget(hline())
        footer = QHBoxLayout()

        # Spacer item pushes the buttons to the right
        footer.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        ))

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.setStyleSheet(
            "QPushButton { background-color: #333333; }"
            "QPushButton:hover { background-color: #444444; }"
        )
        self.cancel_btn.clicked.connect(self.reject)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save_clicked)

        # Add both buttons to the footer layout
        footer.addWidget(self.cancel_btn)
        footer.addWidget(self.save_btn)

        # Add the footer layout to the root layout
        self._root_layout.addLayout(footer)

        # Dictionary for storing field widgets by name.
        #   key:   string name like "part_number"
        #   value: widget instance like QLineEdit
        self._fields: Dict[str, QWidget] = {}

    # Add field helpers ------------------------------------------------------------------------
    def add_line_edit(self, label: str, name: str, placeholder: str = "") -> QLineEdit:
    # Add a single-line text box to the form; 'label' (text shown to user), 'name' (internal
    # key, used with _get() / _set()), 'placeholder' (grey hint text inside text box).
        le = QLineEdit()
        if placeholder:
            le.setPlaceholderText(placeholder)

        # Add row: (QLabel(label), QLineEdit)
        self._form_layout.addRow(QLabel(label), le)

        # Store this widget in the field dictionary for later access
        self._fields[name] = le
        return le

    def add_text_edit(self, label: str, name: str, min_rows: int = 4) -> QTextEdit:
    # Add multi-line text box (comments, notes, etc). mini_rows is used to set approx
     # minimum height.
        te = QTextEdit()
        te.setMinimumHeight(int(min_rows * 20))

        self._form_layout.addRow(QLabel(label), te)
        self._fields[name] = te

        return te

    def add_combo(self, label: str, name: str, items: list[str],
                  current: Optional[str] = None) -> QComboBox:
    # Add drop-down list with given items; 'items' (list of strings to show in dialog),
    # 'current' (optional default section).
        cb = QComboBox()
        cb.addItems(items)

        # If a default 'current' is provided and exists, select it
        if current and current in items:
            cb.setCurrentText(current)
        self._form_layout.addRow(QLabel(label), cb)
        self._fields[name] = cb
        return cb

    def add_date(self, label: str, name: str, value: Optional[str] = None) -> QDateEdit:
        # Add date picker field (default: uses today's date). If value is given as YYYY-MM-DD, try
        # to set that date.
        de = QDateEdit()
        de.setCalendarPopup(True)
        de.setDisplayFormat("yyyy-MM-dd")
        de.setDate(QDate.currentDate())

        if value:
            try:
                # Try to split the string and convert to integers
                y, m, d = [int(x) for x in str(value).split("-")]
                de.setDate(QDate(y, m, d))
            except Exception:
                # If parsing fails, silently ignore and keep default date
                pass

        self._form_layout.addRow(QLabel(label), de)
        self._fields[name] = de
        return de

    def add_time(self, label: str, name: str, value: Optional[str] = None) -> QTimeEdit:
        # Add time picker field (current time by default). If 'value' is given as HH:MM,
        # try to set that time.
        te = QTimeEdit()
        te.setDisplayFormat("HH:mm")
        te.setTime(QTime.currentTime())

        if value:
            try:
                # Extract hour and minute values
                hh, mm = [int(x) for x in str(value).split(":")[:2]]
                te.setTime(QTime(hh, mm))
            except Exception:
                # If parsing fails, just ignore and keep default
                pass

        self._form_layout.addRow(QLabel(label), te)
        self._fields[name] = te
        return te

    def add_separator(self, text: Optional[str] = None):
        # Add a horizontal separator line, optionally with a text heading above it.

        if text:
            lbl = QLabel(text)
            lbl.setStyleSheet('font: bold 14px "Segoe UI"; color:#cccccc')
            self._root_layout.addWidget(lbl)
        self._root_layout.addWidget(hline())

    # Value helpers -------------------------------------------------------------------------
    def _get(self, name: str) -> Any:
    # Get current value of field id'd by 'name'. Return type depends on widget type:
    # QLineEdit (string), QTextEdit (string [all text]), QComboBox (selected item [string]),
    # QdateEdit (string "YYYY-MM-DD"), QTimeEdit (string "HH:MM").
        w = self._fields.get(name)
        if isinstance(w, QLineEdit):
            return w.text()
        if isinstance(w, QTextEdit):
            return w.toPlainText()
        if isinstance(w, QComboBox):
            return w.currentText()
        if isinstance(w, QDateEdit):
            return w.date().toString("yyyy-MM-dd")
        if isinstance(w, QTimeEdit):
            return w.time().toString("HH:mm")
        # If the field name is unknown or widget type unhandled:
        return None

    def _set(self, name: str, value: Any):
    # Set the value of a field based on its 'name' (for when editing an existing
    # record: loads values from db and pushes them into the widgets).
        w = self._fields.get(name)
        if isinstance(w, QLineEdit):
            # Convert None to empty string; others to string
            w.setText("" if value is None else str(value))
        elif isinstance(w, QTextEdit):
            w.setPlainText("" if value is None else str(value))
        elif isinstance(w, QComboBox):
            # Only set if the value matches one of the items
            if value in [w.itemText(i) for i in range(w.count())]:
                w.setCurrentText(value)
        elif isinstance(w, QDateEdit) and value:
            try:
                y, m, d = [int(x) for x in str(value).split("-")]
                w.setDate(QDate(y, m, d))
            except Exception:
                pass
        elif isinstance(w, QTimeEdit) and value:
            try:
                hh, mm = [int(x) for x in str(value).split(":")[:2]]
                w.setTime(QTime(hh, mm))
            except Exception:
                pass

    # Saving ---------------------------------------------------------------------------------
    def _on_save_clicked(self):
    # Int. handler connected to 'Save' btn. Calls self.on_save_clicked()-- overridden by
     # child classes. If that returns 'True', dialog is closed. If exception raised, error
    # popup opens.
        try:
            if self.on_save_clicked():
                self.accept()
        except Exception as e:
            # Show error dialog instead of crashing
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def on_save_clicked(self) -> bool:
    # Placeholder method-- to be overridden by subclasses, which implement this and
     # return 'True' to close dialog, or 'False' to keep dialog open (e.g., validation
    # failed).
        return True