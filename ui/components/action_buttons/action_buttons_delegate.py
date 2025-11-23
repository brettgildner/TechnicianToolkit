from __future__ import annotations
from typing import Callable, Optional, Dict, Tuple
from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QApplication

"""
This module implements a custom ActionButtonsDelegate used to draw small inline action buttons
such as Edit, Delete, and Order—directly inside table cells of a QTableView. The delegate handles 
button layout, painting, hover highlighting, and click detection, while mapping clicks back to the 
correct underlying model row, even when proxy models are used. By storing per-cell button hit-areas 
and triggering user-provided callback functions, it provides a clean, reusable way to embed 
interactive row-level controls within any table-based interface.

ui.components.action_buttons.action_buttons_delegate.py index:

class ActionButtonsDelegate(): Draws small inline action buttons inside a QTableView cell
 - def __init__(): Initializes ActionButtonsDelegate
 - def compute_actions_width(): Returns width needed to fit given # of action buttons
 - def required_width(): Convenience wrapper — returns the exact Actions column width
 - def paint(): Draws the button shapes and text
    - def draw_btn(): Helper: Draw a single mini button
 - def editorEvent(): Checks if user hovered or clicked a button
"""

class ActionButtonsDelegate(QStyledItemDelegate):
# Draws small inline action buttons inside a QTableView cell; supports up to
# three mini-buttons: 'edit' (blue), 'delete' (red), and 'order' (green).
    def __init__(
        self,
        parent=None,
        button_keys: list[str] | None = None,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_order: Optional[Callable[[int], None]] = None,
    ):
        super().__init__(parent)
        self.button_keys = button_keys or ["edit", "delete"]
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_order = on_order

        self._rects: Dict[Tuple[int, int], Dict[str, QRect]] = {}

        # Tracks which button the mouse is hovering over
        # Stored as: (row, "edit") or None
        self._hovered_button: Optional[Tuple[int, str]] = None

    # Button size calculation for column auto-sizing
    @staticmethod
    def compute_actions_width(button_count: int) -> int:
        # Returns width needed to fit given # of action buttons drawn by this delegate.

        btn_width = 64
        spacing = 6
        total_width = btn_width * button_count + spacing * (button_count + 1)
        return total_width + 10

    def required_width(self) -> int:
        return self.compute_actions_width(len(self.button_keys))

    def paint(self, painter: QPainter, option, index):
        rect = option.rect
        row = index.row()
        col = index.column()

        h = 24
        spacing = 6
        btn_width = 64
        x = rect.x() + spacing
        y = rect.y() + (rect.height() - h) // 2

        # Dictionary to store the button rectangles for THIS cell
        rects_for_cell: Dict[str, QRect] = {}

        # Create rectangles for each requested button in order
        for key in self.button_keys:
            btn_rect = QRect(x, y, btn_width, h)
            rects_for_cell[key] = btn_rect
            x = btn_rect.right() + spacing

        # Store the rectangles for hit detection later
        self._rects[(row, col)] = rects_for_cell

        # Begin painting
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Helper: Draw a single mini button
        def draw_btn(btn_key: str, text: str, base: str, hover: str):
            btn_rect = rects_for_cell[btn_key]

            hovered = (self._hovered_button == (row, btn_key))
            color = QColor(hover if hovered else base)

            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(btn_rect, 6, 6)

            painter.setPen(Qt.white)
            painter.drawText(btn_rect, Qt.AlignCenter, text)

        # Draw buttons according to the keys
        for key in self.button_keys:
            if key == "order":
                draw_btn("order", "Order", "#00994d", "#00cc66")  # green
            elif key == "edit":
                draw_btn("edit", "Edit", "#0066cc", "#3399ff")    # blue
            elif key == "delete":
                draw_btn("delete", "Delete", "#cc0000", "#ff3333") # red

        painter.restore()

    # Check if user hovered/clicked button
    def editorEvent(self, event, model, option, index):
        key = (index.row(), index.column())

        # If no rects exist for this cell, ignore the event
        if key not in self._rects:
            return False

        rects = self._rects[key]
        pos = event.pos()
        etype = event.type()

        # Mouse hover highlight
        if etype == QEvent.Type.MouseMove:
            new_hover: Optional[Tuple[int, str]] = None

            # Determine which (if any) button the mouse is over
            for btn_key, r in rects.items():
                if r.contains(pos):
                    new_hover = (index.row(), btn_key)
                    break

            # Only update if it actually changed
            if new_hover != self._hovered_button:
                self._hovered_button = new_hover

                # Redraw table viewport to show hover highlight
                if isinstance(self.parent(), QTableView):
                    self.parent().viewport().update()
            return False

        # Upon mouse leave remove hover highlight
        if etype == QEvent.Type.Leave:
            if self._hovered_button is not None:
                self._hovered_button = None
                if isinstance(self.parent(), QTableView):
                    self.parent().viewport().update()
            return False

        # Detect click upon mouse button release
        if etype == QEvent.Type.MouseButtonRelease:
            view = self.parent()
            if not isinstance(view, QTableView):
                return False

            # If proxy model exists, translate to source index
            proxy = view.model()
            if hasattr(proxy, "mapToSource"):
                src_index = proxy.mapToSource(index)
                src_row = src_index.row()
            else:
                src_row = index.row()

            # Determine which button was clicked
            clicked_key: Optional[str] = None
            for btn_key, r in rects.items():
                if r.contains(pos):
                    clicked_key = btn_key
                    break

            # If no button was actually clicked, ignore the event
            if not clicked_key:
                return False
            QApplication.beep()

            # Execute the matching callback
            if clicked_key == "order" and self.on_order:
                self.on_order(src_row)
            elif clicked_key == "edit" and self.on_edit:
                self.on_edit(src_row)
            elif clicked_key == "delete" and self.on_delete:
                self.on_delete(src_row)
            return True
        return False