from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QWidget, QAbstractItemDelegate
import sqlite3

"""
Custom Qt item delegate for selecting part numbers inside a table view.

This module defines `PartComboDelegate`, a QStyledItemDelegate subclass that
provides a QComboBox editor populated with part numbers retrieved from the
inventory database. It is used to allow users to choose a valid part directly
from a dropdown within a table cell.

Key responsibilities:
- Create a QComboBox editor populated with parts from `inventory_items`.
- Prevent automatic or unintended commits by tracking real user interactions.
- Handle the full Qt delegate lifecycle (createEditor, setEditorData,
  setModelData, updateEditorGeometry, eventFilter).
- Emit commit signals only when the user intentionally selects an item.

This delegate is typically installed on a column of a QTableView where part
selection is required.

ui.components.part_combo_delegate.py index:
class PartComboDelegate: Retrieves part #'s from inventory for drop-down 'part replaced' cell in SA
 - def __init__(): Stores the database path and initializes the delegate’s state.
 - def createEditor(): Builds the combo box editor and populates it with part numbers from the database.
 - def _on_user_activated(): Marks that the user has actively selected a value in the dropdown.
 - def commitAndCloseEditor(): Commits the current dropdown value to the model and closes the editor.
 - def setEditorData(): Preloads the editor with the cell’s existing value when editing starts.
 - def setModelData(): Writes the selected part number from the editor back into the model.
 - def updateEditorGeometry(): Sizes and positions the editor to match the table cell.
 - def eventFilter(): Controls commit behavior on focus changes, prevents accidental auto-commits
"""

class PartComboDelegate(QStyledItemDelegate):
# Retrieves part #'s from inventory for drop-down 'part replaced' cell in SA
    commitData = Signal(QWidget)

    def __init__(self, db_path, parent=None):
    # Stores the database path and initializes the delegate’s state.
        super().__init__(parent)
        self.db_path = db_path
        self._user_interacted = False  # NEW FLAG

    def createEditor(self, parent, option, index):
    # Builds the combo box editor and populates it with part numbers from the database.
        print("DEBUG: PartComboDelegate.createEditor at row", index.row())
        editor = QComboBox(parent)

        # Add blank option at the top
        editor.addItem("")  # appears empty in dropdown
        editor.setCurrentIndex(-1)  # no default selection

        # Load parts from DB
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("SELECT part_number FROM inventory_items WHERE quantity > 0")
            parts = cur.fetchall()
        except Exception as e:
            print("DEBUG: ERROR loading parts from inventory_items:", e)
            parts = []
        conn.close()

        for (pn,) in parts:
            editor.addItem(pn)

        # Pure user action tracking
        editor.activated.connect(self._on_user_activated)

        editor.installEventFilter(self)
        self._user_interacted = False
        return editor

    def _on_user_activated(self, index):
    # Called only when user actually picks a value.
        self._user_interacted = True

    def commitAndCloseEditor(self, editor):
    # Commits the current dropdown value to the model and closes the editor.
        value = editor.currentText()
        print("DEBUG: commitAndCloseEditor fired with value:", value)
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)

    def setEditorData(self, editor, index):
    # Preloads the editor with the cell’s existing value when editing starts.
        value = index.data(Qt.EditRole)
        print("DEBUG: setEditorData, current cell value:", value)

        if value is None or value == "":
            # select the blank option
            editor.setCurrentIndex(0)
            return

        i = editor.findText(value)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
    # Writes the selected part number from the editor back into the model.
        value = editor.currentText()
        print("DEBUG: delegate.setModelData called, setting:", value)
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
    # Sizes and positions the editor to match the table cell
        editor.setGeometry(option.rect)

    def eventFilter(self, editor, event):
    # Prevent autopopulate because of premature FocusOut
        if event.type() == QEvent.FocusOut:
            print("DEBUG: FocusOut - user_interacted =", self._user_interacted)

            if self._user_interacted:
                # Commit ONLY if user actually interacted
                self.commitAndCloseEditor(editor)
            else:
                print("DEBUG: Ignoring FocusOut commit (no user interaction)")

            return False

        return super().eventFilter(editor, event)




