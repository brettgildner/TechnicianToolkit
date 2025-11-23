from __future__ import annotations
from typing import Callable, Optional, Any
from PySide6.QtWidgets import QWidget, QMessageBox
from core.logic import get_current_user
from core.models.parts_model import PartsOrder
from ui.forms.base_dialog_form import BaseDialogForm

"""
This page defines the order confirmation form that appears when a user initiates a parts order from 
an inventory item. The form, built on BaseDialogForm, displays editable fields pre-filled from the 
selected inventory record—such as part number, model, description, and quantity. When submitted, it 
validates the quantity and then creates a new PartsOrder database entry. An optional callback can be 
run afterward to refresh the UI or perform follow-up actions.
"""

# Order Confirmation (from Inventory row)
class OrderConfirmationForm(BaseDialogForm):
    def __init__(self, parent: Optional[QWidget], inventory_item: Any,
                 on_save: Optional[Callable[[], None]] = None):
        super().__init__(parent, title="Confirm Parts Order", width=420, height=520)
        self.item = inventory_item
        self._after_save = on_save

        # Pre-filled, but editable fields:
        self.add_line_edit("Part Number", "part_number")
        self.add_line_edit("Model", "model")
        self.add_line_edit("Description", "description")
        self.add_line_edit("Order Quantity", "quantity")

        # Pull defaults from the inventory_item object.
        # getattr is used with defaults in case some attributes are missing.
        self._set("part_number", getattr(self.item, "part_number", ""))
        self._set("model", getattr(self.item, "model", ""))
        self._set("description", getattr(self.item, "part_description", ""))
        self._set("quantity", str(getattr(self.item, "quantity", 1)))
        self.show()

    def on_save_clicked(self) -> bool:
        # Create a PartsOrder based on the values in this form.

        user = get_current_user() or "default_user"
        qty_s = (self._get("quantity") or "").strip()

        # Validate quantity: must be a positive integer
        try:
            qty = int(qty_s)
            if qty <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Quantity",
                "Please enter a positive integer for quantity."
            )
            return False

        # Actually create a PartsOrder row in the database
        PartsOrder.create(
            quantity=qty,
            part_number=(self._get("part_number") or "").strip(),
            model=(self._get("model") or "").strip(),
            description=(self._get("description") or "").strip(),
            user=user,
        )

        if self._after_save:
            self._after_save()
        return True
