from __future__ import annotations
from typing import Callable, Optional, Any
from PySide6.QtWidgets import QWidget
from core.logic import get_current_user
from core.models.inventory_model import InventoryItem
from ui.forms.base_dialog_form import BaseDialogForm

"""
This page defines the form used to create or edit inventory items within the application. Built on 
the shared BaseDialogForm, it presents fields for part numbers, quantities, locations, model details, 
descriptions, verification dates, and categories. When editing, it pre-populates the UI with existing 
values; when saving, it gathers all inputs and either updates an existing InventoryItem record or 
creates a new one. It also optionally triggers a callback so the rest of the UI can refresh after 
changes.
"""

# Inventory Form
class InventoryForm(BaseDialogForm):
    def __init__(self, parent: Optional[QWidget] = None, item: Optional[Any] = None,
                 on_save: Optional[Callable[[], None]] = None):
        # Initialize BaseDialogForm with title and size
        super().__init__(parent, title="Inventory Item", width=650, height=520)
        self.item = item
        self._after_save = on_save

        # Add each field to the form
        self.add_line_edit("Part Number", "part_number")
        self.add_line_edit("Quantity", "quantity")
        self.add_line_edit("Location", "part_location")
        self.add_line_edit("Model", "model")
        self.add_line_edit("Description", "part_description")
        self.add_date("Verification Date", "verification_date")
        self.add_combo("Category", "category_id", ["parts", "consumables"])

        # If an existing item was provided, populate the fields with its data
        if item:
            self._set("part_number", item.part_number)
            self._set("quantity", item.quantity)
            self._set("part_location", item.part_location)
            self._set("model", item.model)
            self._set("part_description", item.part_description)

            # Some attributes may be missing, use getattr with default None
            if getattr(item, "quarterly_inventory_verification_date", None):
                self._set("verification_date", item.quarterly_inventory_verification_date)
            if getattr(item, "category_id", None):
                self._set("category_id", item.category_id)

        self.show()  # Show the dialog (non-blocking modal)

    def on_save_clicked(self) -> bool:
        # Collect values from the form and insert/update the InventoryItem record.
        data = {
            "part_number": self._get("part_number"),
            "quantity": self._get("quantity"),
            "part_location": self._get("part_location"),
            "model": self._get("model"),
            "part_description": self._get("part_description"),
            "quarterly_inventory_verification_date": self._get("verification_date"),
            "category_id": self._get("category_id"),
            "user": get_current_user() or "default_user",
        }

        # When editing an existing item, update it; otherwise, create a new one.
        if self.item:
            InventoryItem.update(self.item.id, **data)
        else:
            InventoryItem.create(**data)

        # If a callback was provided, call it now (e.g. refresh a table)
        if self._after_save:
            self._after_save()
        return True   # Returning True means “close this dialog”