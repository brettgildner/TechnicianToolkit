from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog

"""
This module defines the ExpenseHelpDialog-- a help window that helps users with key features of 
the Expense Report page. It explains the purpose of the header labeled "Expense Report Info", how
to add and edit expense entries, the process of exporting to Excel (including ensuring the correct
file path and file type), and how to clear monthly entries.
"""

class ExpenseHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help – Expense Report")
        self.resize(650, 720)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Using the Expense Report Page")
        title.setStyleSheet("font: bold 20px 'Segoe UI'; color: #00ff99;")
        layout.addWidget(title)

        # Report Info Section
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Editing Report Information</h3>"
            "<p>The <b>Edit Report Info</b> button opens a window where you enter all "
            "monthly report metadata such as your name, employee number, destination/purpose, "
            "and the report date range.</p>"
            "<ul>"
            "<li>These fields are saved automatically and persist month to month.</li>"
            "<li>The date range determines which expenses are exported.</li>"
            "<li>You may update this information at any time.</li>"
            "</ul>"
            "<p><b>Tip:</b> You only need to update the header information when you are "
            "preparing to export your monthly report.</p>"
        )
        section1.setWordWrap(True)
        section1.setStyleSheet("color: #ddd;")
        layout.addWidget(section1)

        # Adding / Editing Entries
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Adding and Editing Expense Entries</h3>"
            "<p>Use the <b>+ Add Expense</b> button to create a new expense entry. "
            "Each row represents one event such as mileage, lodging, airfare, meals, or "
            "miscellaneous expenses.</p>"
            "<ul>"
            "<li>Double-click a row to edit it.</li>"
            "<li>Use the Edit/Delete icons in the Actions column to modify entries.</li>"
            "<li>Miles, lodging, airfare, and all other values accept standard numeric input.</li>"
            "<li>Blank rows are never added; all entries must have a valid date.</li>"
            "</ul>"
        )
        section2.setWordWrap(True)
        section2.setStyleSheet("color: #ddd;")
        layout.addWidget(section2)

        # Exporting
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Exporting to Excel</h3>"
            "<p>The <b>Export to Excel</b> button fills your data into a preformatted "
            "Expense Report template.</p>"
            "<ul>"
            "<li>Only entries within the selected <b>Begin</b> and <b>End</b> dates are exported.</li>"
            "<li>Make sure your header information is complete before exporting.</li>"
            "<li>The saved file is a fully formatted official expense report.</li>"
            "</ul>"
        )
        section3.setWordWrap(True)
        section3.setStyleSheet("color: #ddd;")
        layout.addWidget(section3)

        # Setting Up Export to Excel
        section3b = QLabel(
            "<h4 style='color:#00ff99; margin-top:10px;'>Setting Up Export to Excel</h4>"
            "<p>The Expense Report exporter uses a <b>blank monthly template</b> that you must "
            "save on your computer before your first export.</p>"
            "<p><b>Setup steps:</b></p>"
            "<ol>"
            "<li>Locate the blank <b>Mileage Expense Form</b> provided by your administrator.</li>"
            "<li>Save a clean copy somewhere easy to find.</li>"
            "<li>Select this file when you click <b>Export to Excel</b>.</li>"
            "<li>The exporter fills in the sheet automatically.</li>"
            "<li>Update the label to match the <b>month and year</b>.</li>"
            "</ol>"
        )
        section3b.setWordWrap(True)
        section3b.setStyleSheet("color: #ddd;")
        layout.addWidget(section3b)

        # Recommended Workflow
        section3c = QLabel(
            "<h4 style='color:#00ff99; margin-top:10px;'>Recommended Workflow</h4>"
            "<p>To make reporting fast and clean, follow this workflow:</p>"
            "<ul>"
            "<li>Create folder <b>Expense Reports</b>.</li>"
            "<li>Place your blank template inside a <b>Templates</b> folder.</li>"
            "<li>Each month, choose that template when exporting.</li>"
            "<li>Rename the output file appropriately (e.g., January 2026).</li>"
            "</ul>"
        )
        section3c.setWordWrap(True)
        section3c.setStyleSheet("color: #ddd;")
        layout.addWidget(section3c)

        # Clearing Entries
        section4 = QLabel(
            "<h3 style='color:#00ff99;'>Clearing Monthly Entries</h3>"
            "<p>The <b>Clear All Entries</b> button removes all saved expense lines "
            "for the current user.</p>"
            "<ul>"
            "<li>Use this at the beginning of a new month.</li>"
            "<li>You will be asked to confirm.</li>"
            "<li>This does not delete header information.</li>"
            "</ul>"
        )
        section4.setWordWrap(True)
        section4.setStyleSheet("color: #ddd;")
        layout.addWidget(section4)

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
