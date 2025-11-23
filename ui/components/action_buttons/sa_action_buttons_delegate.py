from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, QRect, QEvent, QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QApplication

"""
This module implements the SAActionButtonDelegate, a custom delegate used in the Service Activity table 
to display inline Edit and Delete buttons within each row’s Actions column. It draws the colored buttons 
with hover effects, stores their on-screen geometry for accurate hit detection, and interprets mouse 
events to determine when a button is hovered or clicked. When a click occurs, the delegate maps the index 
back to the underlying source model and triggers the corresponding callback provided by the Service 
Activity page. This keeps the UI responsive and interactive while keeping the delegate focused solely on 
visual rendering and event handling.

ui.components.action_buttons.sa_action_button_delegate.py index:

class SAActionButtonDelegate(): Delegate for Service Activity actions column.
 - def __init__(): Store callbacks and setup state.
 - def paint(): Draws the button shapes and text
     - def draw_btn(): Helper: Draw a single mini button
 - def editorEvent(): hover + click detection

"""

class SAActionButtonDelegate(QStyledItemDelegate):
    # Responsible for drawing & interacting with the 'Actions' column. Paints two
    # colored buttons in each cell, adds hover highlight, detects mouse-clicking
    # and calling callbacks with the correct row. Doesn't talk to the db, know
    # anything about ServiceActivity, and only calls the provided callbacks with
    # source_row index.

    def __init__(self, parent=None, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._rects: dict[tuple[int, int], dict[str, QRect]] = {}
        self._hovered: Optional[tuple[int, str]] = None

    # Painting the mini-buttons
    def paint(self, painter: QPainter, option, index: QModelIndex):
        rect = option.rect
        h = 26
        w = 64
        spacing = 8
        y = rect.y() + (rect.height() - h) // 2

        # Calculate the rectangles where "Edit" and "Delete" will be drawn.
        edit_rect = QRect(rect.x() + spacing, y, w, h)
        del_rect = QRect(edit_rect.right() + spacing, y, w, h)

        # Cache these rectangles for this particular table cell.
        self._rects[(index.row(), index.column())] = {
            "edit": edit_rect,
            "delete": del_rect,
        }

        # Helper for drawing a single button.
        def draw_btn(r: QRect, text: str, base: str, hover: str, key: str):
            # Determine if THIS button is the one the mouse is currently over.
            hovered = (self._hovered == (index.row(), key))
            color = QColor(hover if hovered else base)

            painter.save()
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, 6, 6)
            painter.setPen(Qt.white)
            painter.drawText(r, Qt.AlignCenter, text)
            painter.restore()

        # Draw Edit (blue) and Delete (red) buttons.
        draw_btn(edit_rect, "Edit", "#0066cc", "#3399ff", "edit")
        draw_btn(del_rect, "Delete", "#cc0000", "#ff3333", "delete")

    # Mouse / hover events for the buttons
    def editorEvent(self, event, model, option, index: QModelIndex):
        key = (index.row(), index.column())
        if key not in self._rects:
            return False

        rmap = self._rects[key]
        pos = event.pos()
        etype = event.type()

        # Hover handling
        if etype == QEvent.MouseMove:
            new_hover: Optional[tuple[int, str]] = None
            # Check which, if any, button contains the mouse position.
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    new_hover = (index.row(), btn_key)
                    break

            # Only update if hover target changed > prevents unnecessary repaints.
            if new_hover != self._hovered:
                self._hovered = new_hover
                if self.parent():
                    # Request a repaint of the table's visible area.
                    self.parent().viewport().update()
            return False

        if etype == QEvent.Leave:
            # Mouse left the cell: clear hover.
            if self._hovered is not None:
                self._hovered = None
                if self.parent():
                    self.parent().viewport().update()
            return False

        # Click handling
        if etype == QEvent.MouseButtonRelease:
            view = self.parent()
            if not isinstance(view, QTableView):
                return False

            proxy = view.model()
            if not isinstance(proxy, QSortFilterProxyModel):
                return False

            # Map from proxied row/col back to the underlying source row.
            source_index = proxy.mapToSource(index)
            source_row = source_index.row()

            # Determine which button was clicked at that coordinate.
            clicked: Optional[str] = None
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    clicked = btn_key
                    break

            if clicked:
                QApplication.beep()
                # Call the appropriate callback with the row in the base model.
                if clicked == "edit" and self.on_edit:
                    self.on_edit(source_row)
                elif clicked == "delete" and self.on_delete:
                    self.on_delete(source_row)
                return True
        return super().editorEvent(event, model, option, index)