from __future__ import annotations
from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QApplication

"""
This module implements the InventoryActionButtonDelegate, a custom table-cell delegate that renders 
Order, Edit, and Delete action buttons inside the inventory table’s “Actions” column. It draws the 
colored mini-buttons, tracks hover states for visual feedback, records each button’s position for 
precise click detection, and maps user clicks back to the correct source-model row. When a button is 
clicked, the delegate triggers the corresponding callback provided by the Inventory page, allowing 
inline row-level actions to be performed seamlessly within the table.

ui.components.action_buttons.inventory_action_buttons_delegate.py index:

class InventoryActionButtonDelegate(): Responsible for drawing the 'Order', 'Edit', 'Delete' buttons
 - def __init__(): Initializes InventoryActionButtonDelegate
 - def paint(): Draws the button shapes and text
     - def draw_btn(): Helper: Draw a single mini button
 - def editorEvent(): hover + click detection
"""

# Actions column delegate; responsible for drawing the 'Order', 'Edit', 'Delete' buttons in the
# 'actions' column & detecting which was clicked/hovered.
class InventoryActionButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, on_order=None, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.on_order = on_order
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._rects: dict[tuple[int, int], dict[str, QRect]] = {}
        self._hovered_button = None

    def paint(self, painter, option, index):
        # Draw 'Order', 'Edit', 'Delete' buttons in 'Actions' column;

        # Make sure attributes exist
        if not hasattr(self, "on_order"):
            self.on_order = None
        if not hasattr(self, "on_edit"):
            self.on_edit = None
        if not hasattr(self, "on_delete"):
            self.on_delete = None

        rect = option.rect
        h, w, spacing = 26, 64, 8
        y = rect.y() + (rect.height() - h) // 2

        # Compute each button's rectangle
        order_rect = QRect(rect.x() + spacing, y, w, h)
        edit_rect = QRect(order_rect.right() + spacing, y, w, h)
        del_rect = QRect(edit_rect.right() + spacing, y, w, h)
        self._rects[(index.row(), index.column())] = {
            "order": order_rect,
            "edit": edit_rect,
            "delete": del_rect,
        }

        def draw_btn(r: QRect, text: str, base_color: str, hover_color: str, btn_key: str):
            # Helper to draw a single rounded button with hover effect.
            hovered = (self._hovered_button == (index.row(), btn_key))
            color = QColor(hover_color if hovered else base_color)
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, 6, 6)
            painter.setPen(Qt.white)
            painter.drawText(r, Qt.AlignCenter, text)
            painter.restore()

        # Draw the 3 buttons with different color themes.
        draw_btn(order_rect, "Order", "#00994d", "#00cc66", "order")
        draw_btn(edit_rect, "Edit", "#0066cc", "#3399ff", "edit")
        draw_btn(del_rect, "Delete", "#cc0000", "#ff3333", "delete")

    def editorEvent(self, event, model, option, index):
    # Updates which button is hovered, detects which button was clicked, calls the correct clickback in InventoryPage.

        key = (index.row(), index.column())
        if key not in self._rects:
            return False
        pos = event.pos()
        rmap = self._rects[key]

        # Mouse moved over cell
        if event.type() == QEvent.MouseMove:
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    if self._hovered_button != (index.row(), btn_key):
                        # Remember which button is hovered and repaint cell.
                        self._hovered_button = (index.row(), btn_key)
                        self.parent().viewport().update()
                    break
            return False

        # Mouse left the cell
        if event.type() == QEvent.Leave:
            if self._hovered_button is not None:
                self._hovered_button = None
                self.parent().viewport().update()
            return False

        # User released mouse button
        if event.type() == QEvent.MouseButtonRelease:
            view = self.parent()
            if not isinstance(view, QTableView):
                return False

            proxy = view.model()
            source_index = proxy.mapToSource(index)
            source_row = source_index.row()

            # Determine which specific mini-button was clicked.
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    QApplication.beep()
                    if btn_key == "order" and self.on_order:
                        self.on_order(source_row)
                    elif btn_key == "edit" and self.on_edit:
                        self.on_edit(source_row)
                    elif btn_key == "delete" and self.on_delete:
                        self.on_delete(source_row)
                    return True
        return super().editorEvent(event, model, option, index)