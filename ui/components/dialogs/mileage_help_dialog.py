from __future__ import annotations
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

"""
This module defines the MileageHelpDialog-- a help window that assists users with key features of 
the Mileage Tracker page. It explains the purpose of the header labeled "Mileage Report Info", how
to add and edit trips, the process of exporting to Excel (including ensuring the correct
file path and file type), how to clear monthly entries, and how to filter the mileage records if
needed.
"""

class MileageHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help – Mileage Tracker")
        self.resize(650, 520)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Using the Mileage Tracker Page")
        title.setStyleSheet("font: bold 20px 'Segoe UI'; color: #00ff99;")
        layout.addWidget(title)

        # Header Information (Vehicle & Employee Info)
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Header Information</h3>"
            "<p>The header fields at the top of the Mileage Tracker page allow you to "
            "enter employee, vehicle, and date range information that will be used "
            "only when exporting to the official Mileage Expense Report template.</p>"
            "<ul>"
            "<li>These fields are <b>not stored in the database</b>.</li>"
            "<li>You only need to fill them in when you're ready to <b>export your monthly mileage</b>.</li>"
            "<li>Leave them blank while entering mileage throughout the month – it's perfectly fine.</li>"
            "<li>When exporting, each field is sent to the matching location inside the template.</li>"
            "<li>The Begin/End Dates filter which entries will be included in the exported report.</li>"
            "</ul>"
        )
        section1.setWordWrap(True)
        section1.setStyleSheet("color: #ddd;")
        layout.addWidget(section1)

        # Adding & Editing Mileage Entries
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Adding and Editing Entries</h3>"
            "<p>You can log your mileage for each trip using the <b>Add Mileage Entry</b> button.</p>"
            "<ul>"
            "<li>Enter Date, Start Miles, End Miles, Start/End Locations, and Purpose.</li>"
            "<li>Double-click any row to edit an entry.</li>"
            "<li>Use the Delete button to remove an entry.</li>"
            "<li>The table automatically calculates miles driven (End – Start).</li>"
            "</ul>"
            "<p>Your mileage entries are <b>saved in the database</b> so they remain even after restarting the app.</p>"
        )
        section2.setWordWrap(True)
        section2.setStyleSheet("color: #ddd;")
        layout.addWidget(section2)

        # Filtering Mileage Entries
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Filtering Your Mileage Records</h3>"
            "<p>The <b>Filters</b> button opens a simple filter window that lets you show only "
            "the entries containing certain text.</p>"
            "<ul>"
            "<li>Choose a column and type text to filter by.</li>"
            "<li>Filters match any part of the value (e.g., typing 'shop' matches 'Shop Visit').</li>"
            "<li>Use the <b>Reset</b> button to clear all filters.</li>"
            "</ul>"
            "<p>You can combine filtering with column sorting to quickly organize your data.</p>"
        )
        section3.setWordWrap(True)
        section3.setStyleSheet("color: #ddd;")
        layout.addWidget(section3)

        # Exporting to Excel
        section4 = QLabel(
            "<h3 style='color:#00ff99;'>Exporting to the Mileage Expense Report</h3>"
            "<p>When you are ready to submit your monthly mileage, click <b>Export to Excel</b>.</p>"
            "<ul>"
            "<li>The system loads the official mileage template from the assets folder.</li>"
            "<li>The header fields (employee, vehicle, date range) are inserted into the template.</li>"
            "<li>Only entries within the selected Begin/End date range are exported.</li>"
            "<li>The template automatically calculates total miles and the reimbursement amount.</li>"
            "<li>You will be prompted to choose where to save the completed report.</li>"
            "</ul>"
            "<p>If no entries match the chosen date range, you will be notified and nothing will be exported.</p>"
        )
        section4.setWordWrap(True)
        section4.setStyleSheet("color: #ddd;")
        layout.addWidget(section4)

        # Clearing All Entries
        section5 = QLabel(
            "<h3 style='color:#00ff99;'>Clearing All Mileage Entries</h3>"
            "<p>The <b>Clear All Entries</b> button permanently deletes every mileage entry of the current user.</p>"
            "<ul>"
            "<li>This does <b>not</b> delete header information (header fields aren't saved anyway).</li>"
            "<li>Use this if you want to reset the mileage list entirely.</li>"
            "<li>A confirmation prompt prevents accidental deletion.</li>"
            "</ul>"
        )
        section5.setWordWrap(True)
        section5.setStyleSheet("color: #ddd;")
        layout.addWidget(section5)

        # Close Button
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(120)
        btn_close.clicked.connect(self.accept)
        btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #fff;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_close)
        layout.addLayout(bottom)
