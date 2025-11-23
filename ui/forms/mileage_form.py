from __future__ import annotations
from typing import Callable, Optional, Any
from PySide6.QtWidgets import QWidget, QMessageBox
from core.logic import get_current_user
from core.models.mileage_model import MileageEntry
from ui.forms.base_dialog_form import BaseDialogForm

"""
This page defines the mileage entry form used to record or edit travel mileage within the application. 
It builds on the shared BaseDialogForm structure and provides fields for date, starting and ending 
mileage, locations, and trip purpose. When editing, the form pre-populates its fields with an existing 
entry; when saving, it validates numeric inputs, ensures logical mileage values, and then creates or 
updates a MileageEntry record. The form also supports an optional callback to refresh the UI after 
saving.
"""

# Mileage Form
class MileageForm(BaseDialogForm):
    def __init__(self,parent: Optional[QWidget] = None,on_save: Optional[Callable[[], None]] = None,
        item: Optional[Any] = None):
        super().__init__(parent, title="Mileage Entry", width=680, height=560)
        self.item = item
        self._after_save = on_save

        # Form fields
        self.add_date("Date", "date")
        self.add_line_edit("Start Miles", "start_miles")
        self.add_line_edit("End Miles", "end_miles")
        self.add_line_edit("Start Location", "start_location")
        self.add_line_edit("End Location", "end_location")
        self.add_line_edit("Purpose", "purpose")

        # Load existing values
        if item:
            self._set("date", item.date)
            self._set("start_miles", str(item.start_miles))
            self._set("end_miles", str(item.end_miles))
            self._set("start_location", item.start_location)
            self._set("end_location", item.end_location)
            self._set("purpose", item.purpose)
        self.show()

    # Save handler
    def on_save_clicked(self) -> bool:
        # Validate fields and create/update MileageEntry.

        # Convert and validate miles input (must be numeric)
        try:
            start_miles = float(self._get("start_miles"))
            end_miles = float(self._get("end_miles"))
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Start and End miles must be numbers."
            )
            return False

        # Basic validation: end miles must be >= start miles
        if end_miles < start_miles:
            QMessageBox.warning(
                self,
                "Invalid Mileage",
                "End miles cannot be less than start miles."
            )
            return False

        user = get_current_user() or "default_user"

        # Convert QDate to ISO string (YYYY-MM-DD) if needed
        date_val = self._get("date")
        # NOTE: With BaseDialogForm._get, date_val is already a string "YYYY-MM-DD",
        # so the hasattr(toString) check is mostly defensive.
        if hasattr(date_val, "toString"):
            date_val = date_val.toString("yyyy-MM-dd")

        if not date_val:
            QMessageBox.warning(
                self,
                "Missing Date",
                "Please select a date."
            )
            return False

        data = {
            "date": date_val,
            "start_miles": start_miles,
            "end_miles": end_miles,
            "start_location": self._get("start_location"),
            "end_location": self._get("end_location"),
            "purpose": self._get("purpose"),
            "user": user,
        }

        try:
            if self.item:
                # UPDATE existing mileage entry
                MileageEntry.update(
                    id=self.item.id,
                    user=user,
                    date=data["date"],
                    start_miles=data["start_miles"],
                    end_miles=data["end_miles"],
                    start_location=data["start_location"],
                    end_location=data["end_location"],
                    purpose=data["purpose"],
                )
            else:
                # CREATE new mileage entry
                MileageEntry.create(
                    date=data["date"],
                    start_miles=data["start_miles"],
                    end_miles=data["end_miles"],
                    start_location=data["start_location"],
                    end_location=data["end_location"],
                    purpose=data["purpose"],
                    user=user,
                )
        except Exception as e:
            QMessageBox.critical(self, "Failed to Save", str(e))
            return False

        if self._after_save:
            self._after_save()
        return True
