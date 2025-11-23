from __future__ import annotations
from PySide6.QtWidgets import QMessageBox
from core.logic import get_current_user
from ui.forms.base_dialog_form import BaseDialogForm

"""
This page defines the form used to create or edit parts orders within the application. Built on the 
shared BaseDialogForm framework, it presents fields for part number, model, description, and quantity, 
and can pre-populate these when editing an existing order. When the user saves, the form validates 
required fields, checks that the quantity is a valid integer, and then either updates an existing 
PartsOrder record or creates a new one. An optional callback can run afterward to refresh related UI 
elements.
"""

# Parts Order Form
class PartsOrderForm(BaseDialogForm):
    def __init__(self, parent=None, item=None, on_save=None):
        super().__init__(parent, title="Parts Order", width=480, height=460)
        self.item = item
        self._after_save = on_save

        # Fields
        self.add_line_edit("Part Number", "part_number")
        self.add_line_edit("Model", "model")
        self.add_line_edit("Description", "description")
        self.add_line_edit("Quantity", "quantity")

        # Populate if editing
        if item:
            self._set("part_number", item.part_number)
            self._set("model", item.model)
            self._set("description", item.description)
            self._set("quantity", str(item.quantity))
        self.show()

    # Save handler
    def on_save_clicked(self) -> bool:
        # Validate fields and create/update PartsOrder.

        from core.models.parts_model import PartsOrder  # Local import to avoid cycles
        user = get_current_user() or "default_user"
        part_number = (self._get("part_number") or "").strip()
        quantity_s = (self._get("quantity") or "").strip()

        # Basic required fields validation
        if not part_number or not quantity_s:
            QMessageBox.warning(
                self,
                "Missing Field",
                "Part Number and Quantity are required."
            )
            return False

        # Validate quantity (must be integer)
        try:
            quantity = int(quantity_s)
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Quantity",
                "Quantity must be a whole number."
            )
            return False

        model = (self._get("model") or "").strip()
        description = (self._get("description") or "").strip()

        # Save to DB
        try:
            if self.item:
                # Update existing order: note positional args usage
                PartsOrder.update(self.item.id,quantity,part_number,model,description)
            else:
                # Create new order
                PartsOrder.create(quantity,part_number,model,description,user)

            if self._after_save:
                self._after_save()
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
            return False