from __future__ import annotations
from typing import Optional, Dict
from PySide6.QtCore import Qt, QRect, QEvent, QModelIndex
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QApplication

"""
This module provides the PartsActionDelegate, a custom item delegate used in the Parts table to 
display inline Edit and Delete buttons within each row’s action column. It draws the buttons with 
hover effects, records their on-screen positions for hit detection, and listens for mouse events 
to determine when the user hovers over or clicks a specific action. When a button is clicked, the 
delegate maps the table index back to the source model and triggers the appropriate callback, 
enabling clean, interactive row-level editing and deletion directly from the table.

ui.components.action_buttons.parts_action_button_delegate.py index:

class PartsActionButtonDelegate(): Delegate for Parts actions column.
 - def __init__(): Initializes PartsActionButtonDelegate
 - def paint(): Draws the button shapes and text
     - def draw_btn(): Helper: Draw a single mini button
 - def editorEvent(): hover + click detection
"""

# Delegate that draws and handles edit/delete buttons.
class PartsActionDelegate(QStyledItemDelegate):

    def __init__(self, parent=None, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.on_edit = on_edit
        self.on_delete = on_delete

        # Stores the clickable rectangles for each row
        self._rects: Dict[tuple[int, int], Dict[str, QRect]] = {}
        self._hovered_button: Optional[tuple[int, str]] = None

    def paint(self, painter: QPainter, option, index: QModelIndex):
        # Draws the Edit and Delete button graphics inside the table cell.

        rect = option.rect
        row = index.row()
        col = index.column()

        # Button sizes and positions
        h = 24
        w = 70
        spacing = 8
        y = rect.y() + (rect.height() - h) // 2

        edit_rect = QRect(rect.x() + spacing, y, w, h)
        del_rect = QRect(edit_rect.right() + spacing, y, w, h)

        # Save button rectangles for click detection later
        self._rects[(row, col)] = {
            "edit": edit_rect,
            "delete": del_rect,
        }

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Helper to draw each button
        def draw_btn(r: QRect, label: str, base: str, hover: str, key: str):
            hovered = (self._hovered_button == (row, key))
            color = QColor(hover if hovered else base)

            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, 6, 6)

            painter.setPen(Qt.white)
            painter.drawText(r, Qt.AlignCenter, label)

        # Draw blue Edit and red Delete buttons
        draw_btn(edit_rect, "Edit", "#0066cc", "#3399ff", "edit")
        draw_btn(del_rect, "Delete", "#cc0000", "#ff3333", "delete")

        painter.restore()

    def editorEvent(self, event, model, option, index: QModelIndex):
        # Handles hover and click events on the drawn buttons.

        key = (index.row(), index.column())
        if key not in self._rects:
            return False

        rmap = self._rects[key]
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()

        # Hover handling
        if event.type() == QEvent.MouseMove:
            new_hover = None
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    new_hover = (index.row(), btn_key)
                    break

            if new_hover != self._hovered_button:
                self._hovered_button = new_hover
                if self.parent() is not None:
                    self.parent().viewport().update()

            return False

        # Mouse left the cell > remove hover highlight
        if event.type() == QEvent.Leave:
            if self._hovered_button is not None:
                self._hovered_button = None
                if self.parent() is not None:
                    self.parent().viewport().update()
            return False

        # Click handling
        if event.type() == QEvent.MouseButtonRelease:
            view = self.parent()

            from PySide6.QtWidgets import QTableView
            if not isinstance(view, QTableView):
                return False

            # Map filtered (proxy) index to source row
            proxy = view.model()
            source_index = proxy.mapToSource(index)
            source_row = source_index.row()

            clicked_key = None
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    clicked_key = btn_key
                    break
            if not clicked_key:
                return False

            QApplication.beep()

            # Fire callbacks
            if clicked_key == "edit" and self.on_edit:
                self.on_edit(source_row)
            elif clicked_key == "delete" and self.on_delete:
                self.on_delete(source_row)
            return True

        return super().editorEvent(event, model, option, index)