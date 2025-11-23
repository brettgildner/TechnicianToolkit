from __future__ import annotations
from typing import Callable, Optional, Any
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtWidgets import (QDialog, QWidget, QLabel, QLineEdit, QTextEdit, QComboBox,
                               QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QScrollArea,
                               QDateEdit, QTimeEdit, QMessageBox)
from core.logic import get_current_user, compute_duration
from core.models.service_activity_model import ServiceActivity
from core.utils import safe_int

"""
This page defines the full service activity entry form used to record, edit, and manage service-related 
work performed on customer equipment. It provides a large, scrollable dialog containing detailed fields 
such as customer info, malfunction codes, remedial actions, part usage, technician notes, timestamps, 
and automatically computed call duration. When editing, it pre-fills all fields from an existing record; 
when saving, it validates inputs, updates or creates a ServiceActivity record, and optionally adjusts 
inventory quantities through the controller. The form supports both creation and modification workflows 
and triggers an optional callback after saving.

ui.forms.service_activity_form.py index:
class ServiceActivityForm():  Dialog for creating/editing service activity records.
- def __init__(): Build form UI and initialize fields.
    - def add_line(): Add single-line text field.
    - def add_text(): Add multi-line text area.
    - def add_combo(): Add dropdown field.
    - def add_date(): Add date picker.
    - def add_time(): Add time picker.
- def _populate(): Fill form fields from existing record.
- def on_save_clicked(): Validate input, update/create service record, adjust inventory, and save.
"""

# Service Activity Form
_MALFUNCTIONS = [
    "01 - Varying Image", "02 - Dark Image", "03 - Light Image", "04 - Deletions",
    "05 - Distorted Image", "06 - Char. Alignment", "07 - Char Add/Drop",
    "08 - Skewed Print", "10 - Data Registration", "11 - Background", "12 - Line Streaks",
    "13 - Spots", "14 - Unfused Copy", "15 - Border Bands", "16 - Mis/Varying Registr.",
    "18 - Broken Part", "19 - CQ Adjustment", "20 - Copy/CRT Displ", "21 - Scorched Print",
    "23 - Print Qual Doc Scan", "24 - System Lockup", "27 - Print Damaged", "29 - Incorrect Color",
    "30 - Paper Handling", "31 - Jams", "32 - Paper Fire", "33 - Improper Feed",
    "34 - No Sample Print", "35 - Multi Sheet Feed", "36 - Skewed Feed",
    "37 - Improper Stack/Sort", "38 - Document Handling", "39 - Document Damaged",
    "40 - Disk Failure", "43 - Oil/Machine Leakage", "44 - Improper Config",
    "47 - Print/Copy Cartridge", "48 - CRU Failure", "49 - ESS Failure",
    "50 - System Rollover Crash", "51 - Host Channel", "52 - Firmware", "53 - Software",
    "54 - Won't Boot Hardware", "55 - Memory Failure", "56 - Smoke", "57 - Welded",
    "58 - Unusual Odor", "60 - Peripherals", "62 - Won't Print", "63 - Read/Write Check Error",
    "64 - Tape Loop/Vacuum", "65 - Disk Can't Locate Track", "66 - Media Speed",
    "67 - False Shutdown", "68 - Mouse/Cursor", "69 - Telephone Line",
    "70 - Unable to Communicate", "71 - No/Incorrect Input Voltage", "72 - Logic Wrong",
    "73 - Can't Select Machine Feature", "74 - Control Failure", "75 - Machine Inoperative",
    "76 - Non-Paper Fire/Smoke", "77 - Abnormal Sound/Vib.", "78 - Developer Leakage",
    "80 - Consumable", "81 - Retraining/Assistance", "82 - Problem Not Observed",
    "85 - Remote Unit Compat.", "86 - Won't Transmit/Receive", "89 - Web Malfunction",
    "90 - Static", "93 - Loose/Broken Hardware", "95 - Head Alignment",
    "96 - No Boot Computer", "97 - Mechanical Adjustment", "98 - Electrical Adjustment",
    "Other"
]
# The last entry "Other" is special: when user selects it, a free-text field appears.

class ServiceActivityForm(QDialog):
    # Dialog that manages service activity entries.

    def __init__(self,parent: Optional[QWidget] = None,on_save: Optional[Callable[[], None]] = None,
        item: Optional[Any] = None):
        super().__init__(parent)
        self.controller = parent.controller if parent and hasattr(parent, "controller") else None

        self.item = item
        self._after_save = on_save
        self.setWindowTitle("Service Activity")
        self.resize(700, 900)
        self.setModal(True)

        # ---------- Scrollable content ----------
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        form_layout = QFormLayout(container)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setSpacing(10)

        # ---------- Field creation helpers ----------
        def add_line(label):
            le = QLineEdit()
            form_layout.addRow(QLabel(label + ":"), le)
            return le

        def add_text(label, rows=3):
            te = QTextEdit()
            te.setFixedHeight(rows * 28)
            form_layout.addRow(QLabel(label + ":"), te)
            return te

        def add_combo(label, items):
            cb = QComboBox()
            cb.addItems(items)
            form_layout.addRow(QLabel(label + ":"), cb)
            return cb

        def add_date(label):
            de = QDateEdit()
            de.setCalendarPopup(True)
            de.setDate(QDate.currentDate())
            form_layout.addRow(QLabel(label + ":"), de)
            return de

        def add_time(label):
            te = QTimeEdit()
            te.setDisplayFormat("HH:mm")
            te.setTime(QTime.currentTime())
            form_layout.addRow(QLabel(label + ":"), te)
            return te

        # ---------- Create fields ----------
        self.area = add_line("Area")
        self.customer = add_line("Customer")
        self.serial_number = add_line("Serial Number")
        self.meter = add_line("Meter")
        self.mal_cb = add_combo("Malfunction", _MALFUNCTIONS)
        self.mal_other = add_line("Malfunction (Other)")
        self.mal_other.setVisible(False)
        self.mal_cb.currentTextChanged.connect(
            lambda text: self.mal_other.setVisible(text == "Other")
        )

        self.remedial_action = add_text("Remedial Action", 4)
        self.quantity = add_line("Quantity")
        self.part_replaced = add_text("Part Replaced", 4)
        self.technician = add_line("Technician")
        self.comments = add_text("Comments", 5)
        self.arrival_date = add_date("Arrival Date")
        self.arrival_time = add_time("Arrival Time (24-hour)")
        self.departure_date = add_date("Departure Date")
        self.departure_time = add_time("Departure Time (24-hour)")

        # ---------- Buttons ----------
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.setStyleSheet(
            "background-color: #00cc88; color: white; "
            "border-radius: 6px; padding: 6px 16px;"
        )
        btn_cancel.setStyleSheet(
            "background-color: #777; color: white; "
            "border-radius: 6px; padding: 6px 16px;"
        )

        btn_save.clicked.connect(self.on_save_clicked)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        form_layout.addRow(btn_layout)

        # ---------- Layout ----------
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # ---------- Load existing data ----------
        if item:
            self._populate(item)

    # Populate fields if editing an existing record
    def _populate(self, item):
        # Fill the form with existing ServiceActivity data.

        self.area.setText(item.area)
        self.customer.setText(item.customer)
        self.serial_number.setText(item.serial_number)
        self.meter.setText(item.meter)
        self.remedial_action.setPlainText(item.remedial_action)
        self.quantity.setText(str(item.quantity))
        self.part_replaced.setPlainText(item.part_replaced)
        self.technician.setText(item.technician)
        self.comments.setPlainText(item.comments)

        # If malfunction is known in _MALFUNCTIONS, select it.
        # Otherwise, treat it as "Other" and fill mal_other field.
        if item.malfunction in _MALFUNCTIONS:
            self.mal_cb.setCurrentText(item.malfunction)
            self.mal_other.setVisible(False)
        else:
            self.mal_cb.setCurrentText("Other")
            self.mal_other.setText(item.malfunction)
            self.mal_other.setVisible(True)

        # parse dates/times safely (they may be strings or QDate/QTime)
        if hasattr(item, "arrival_date"):
            self.arrival_date.setDate(QDate.fromString(
                str(item.arrival_date), "yyyy-MM-dd"
            ))
        if hasattr(item, "departure_date"):
            self.departure_date.setDate(QDate.fromString(
                str(item.departure_date), "yyyy-MM-dd"
            ))
        if hasattr(item, "arrival_time"):
            self.arrival_time.setTime(QTime.fromString(
                str(item.arrival_time), "HH:mm"
            ))
        if hasattr(item, "departure_time"):
            self.departure_time.setTime(QTime.fromString(
                str(item.departure_time), "HH:mm"
            ))

    # Save logic
    def on_save_clicked(self):
        # Determine malfunction
        mal = self.mal_cb.currentText()
        if mal == "Other":
            mal = self.mal_other.text().strip()

        data = {
            "area": self.area.text().strip(),
            "customer": self.customer.text().strip(),
            "serial_number": self.serial_number.text().strip(),
            "meter": self.meter.text().strip(),
            "malfunction": mal,
            "remedial_action": self.remedial_action.toPlainText().strip(),
            "quantity": self.quantity.text().strip(),  # stays string here
            "part_replaced": self.part_replaced.toPlainText().strip(),
            "technician": self.technician.text().strip(),
            "comments": self.comments.toPlainText().strip(),
            "arrival_date": self.arrival_date.date().toString("yyyy-MM-dd"),
            "departure_date": self.departure_date.date().toString("yyyy-MM-dd"),
            "arrival_time": self.arrival_time.time().toString("HH:mm"),
            "departure_time": self.departure_time.time().toString("HH:mm"),
            "call_duration": compute_duration(
                self.arrival_date.date().toString("yyyy-MM-dd"),
                self.arrival_time.time().toString("HH:mm"),
                self.departure_date.date().toString("yyyy-MM-dd"),
                self.departure_time.time().toString("HH:mm"),
            ),
            "user": get_current_user() or "default_user",
        }

        try:
            if self.item:
                sa = ServiceActivity.get_by_id(self.item.id)

                # Ensure controller is present
                sa.controller = self.controller
                if not sa.controller and hasattr(self.parent(), "controller"):
                    sa.controller = self.parent().controller

                #print("DEBUG loaded SA:", sa.__dict__)

                # Capture old values before modifying
                old_quantity = safe_int(sa.quantity)
                old_part = (sa.part_replaced or "").strip()

                # Assign new values
                new_quantity = safe_int(data["quantity"])
                new_part = data["part_replaced"].strip()

                for key, value in data.items():
                    setattr(sa, key, value)

                # Ensure normalized int quantity
                sa.quantity = new_quantity

                #print("DEBUG UPDATED sa:", sa.__dict__)

                # Adjust inventory (only if controller is available)
                if sa.controller and hasattr(sa.controller, "update_inventory_on_service_edit"):

                    try:
                        sa.controller.update_inventory_on_service_edit(
                            old_part=old_part,
                            new_part=new_part,
                            old_qty=old_quantity,
                            new_qty=new_quantity,
                        )
                    except Exception as inv_err:
                        print("Inventory update error:", inv_err)

                # Save to DB
                sa.update()

            else:
                # Create flow
                ServiceActivity.create(**data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save record:\n{e}")
            return False

        if self._after_save:
            self._after_save()

        self.accept()
        return True