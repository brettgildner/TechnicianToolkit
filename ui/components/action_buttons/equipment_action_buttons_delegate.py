from __future__ import annotations
from PySide6.QtCore import Qt, QRect, QEvent, QSortFilterProxyModel
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QApplication

"""
This module provides the EquipmentActionButtonDelegate, a custom table-cell delegate used in the 
Equipment Info interface to render inline Edit, Delete, and Activity buttons directly within a 
QTableView column. It draws the button shapes with hover highlighting, tracks per-cell button 
geometry for accurate hit-testing, and interprets mouse events to detect when the user hovers over 
or clicks one of the actions. When a button is clicked, the delegate maps the view index back to 
the source model and triggers the appropriate callback, allowing the Equipment Info page to perform 
row-level actions seamlessly.

ui.components.action_buttons.equipment_action_buttons_delegate.py index:

class EquipmentActionButtonDelegate(): Delegate for Equipment Info actions column.
 - def __init__(): Initializes EquipmentActionButtonDelegate
 - def paint(): Draws the button shapes and text
     - def draw_btn(): Helper: Draw a single mini button
 - def editorEvent(): hover + click detection
"""

class EquipmentActionButtonDelegate(QStyledItemDelegate):
    # Delegate for Equipment Info actions column. Draws 'Edit', 'Delete', 'Activity'. Calls
    # back into EquipmentInfoPage via: on_edit(row), on_delete(row), on_show_activity(row).

    def __init__(self, parent=None, on_edit=None, on_delete=None, on_show_activity=None):
        super().__init__(parent)
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_show_activity = on_show_activity

        # cache for button rectangles per-cell
        self._rects = {}
        # hovered status
        self._hovered = None

    def paint(self, painter, option, index):
        rect = option.rect
        h = 26
        spacing = 8
        w = 64
        y = rect.y() + (rect.height() - h) // 2

        # Edit button
        edit_rect = QRect(rect.x() + spacing, y, w, h)
        # Delete button
        delete_rect = QRect(edit_rect.right() + spacing, y, w, h)
        # Activity button
        activity_rect = QRect(delete_rect.right() + spacing, y, w + 12, h)

        self._rects[(index.row(), index.column())] = {
            "edit": edit_rect,
            "delete": delete_rect,
            "show_activity": activity_rect,
        }

        def draw_btn(r, text, base, hover, key):
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

        draw_btn(edit_rect, "Edit", "#0066cc", "#3399ff", "edit")
        draw_btn(delete_rect, "Delete", "#cc0000", "#ff3333", "delete")
        draw_btn(activity_rect, "Activity", "#009933", "#33cc66", "show_activity")

    # Hover + click detection
    def editorEvent(self, event, model, option, index):
        key = (index.row(), index.column())
        if key not in self._rects:
            return False

        rmap = self._rects[key]
        pos = event.pos()
        etype = event.type()

        # Hover handling
        if etype == QEvent.MouseMove:
            new_hover = None
            for btn_key, r in rmap.items():
                if r.contains(pos):
                    new_hover = (index.row(), btn_key)
                    break

            if new_hover != self._hovered:
                self._hovered = new_hover
                if self.parent():
                    self.parent().viewport().update()

            return False

        if etype == QEvent.Leave:
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

            source_index = proxy.mapToSource(index)
            source_row = source_index.row()

            clicked = None
            for key, r in rmap.items():
                if r.contains(pos):
                    clicked = key
                    break

            if clicked:
                QApplication.beep()

                if clicked == "edit" and self.on_edit:
                    self.on_edit(source_row)
                elif clicked == "delete" and self.on_delete:
                    self.on_delete(source_row)
                elif clicked == "show_activity" and self.on_show_activity:
                    self.on_show_activity(source_row)

                return True

        return super().editorEvent(event, model, option, index)