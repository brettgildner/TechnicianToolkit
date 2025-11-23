from __future__ import annotations
from typing import Callable, Optional, Any
from PySide6.QtWidgets import QWidget
from core.logic import get_current_user
from ui.forms.base_dialog_form import BaseDialogForm

"""
This page defines the form used for creating or editing equipment records in the application. It 
builds on the shared BaseDialogForm framework to present a structured, styled dialog containing 
fields such as location, contact info, model details, and notes. The form can pre-fill values when 
editing an existing item, and when saved, it collects all field data and either creates a new 
database record or updates an existing one. It optionally triggers a callback after saving, allowing 
the UI to refresh or update other components.
"""

# Equipment Form
class EquipmentForm(BaseDialogForm):
    def __init__(self, parent: Optional[QWidget] = None, item: Optional[Any] = None,
                 on_save: Optional[Callable[[], None]] = None):
        super().__init__(parent, title="Equipment Info", width=650, height=620)
        self.item = item
        self._after_save = on_save

        # Create several standard line edit fields in a loop
        for label, name in [
            ("Area", "area"),
            ("Customer", "customer"),
            ("Building", "building"),
            ("Room", "room"),
            ("Serial Number", "serial_number"),
            ("Model", "model"),
            ("POC", "poc"),
            ("POC Phone", "poc_phone"),
            ("IT Support", "it_support"),
            ("IT Phone", "it_phone"),
        ]:
            self.add_line_edit(label, name)

        # Additional notes field
        self.add_line_edit("Notes / Comments", "notes")

        # If editing an existing item, pre-fill all fields from the object
        if item:
            for name in ["area", "customer", "building", "room", "serial_number", "model",
                         "poc", "poc_phone", "it_support", "it_phone", "notes"]:
                self._set(name, getattr(item, name, ""))
        self.show()

    def on_save_clicked(self) -> bool:
        # Collect values and save EquipmentInfo (create or update).
        from core.models.equipment_model import EquipmentInfo
        data = {
            "area": self._get("area"),
            "customer": self._get("customer"),
            "building": self._get("building"),
            "room": self._get("room"),
            "serial_number": self._get("serial_number"),
            "model": self._get("model"),
            "poc": self._get("poc"),
            "poc_phone": self._get("poc_phone"),
            "it_support": self._get("it_support"),
            "it_phone": self._get("it_phone"),
            "notes": self._get("notes"),
            "user": get_current_user() or "default_user",
        }

        if self.item:
            # Update existing DB record
            EquipmentInfo.update(self.item.id, **data)
        else:
            # Create new DB record
            EquipmentInfo.create(**data)
        if self._after_save:
            self._after_save()
        return True