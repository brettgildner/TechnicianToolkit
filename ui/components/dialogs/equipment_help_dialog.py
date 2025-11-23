from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog

"""
This module defines the EquipmentHelpDialog-- a help window that helps users with key features of 
the Equipment Info page. It explains the bulk Excel import, filtering and column visibility, and 
sorting tools. 
"""

class EquipmentHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help – Equipment Info")
        self.resize(650, 550)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(
            "<div style='margin:0; padding:0;'>"
            "<span style='font-weight:bold; font-size:20px; color:#00ff99;'>"
            "Using the Equipment Info Page"
            "</span>"
            "</div>"
        )
        title.setTextFormat(Qt.RichText)
        layout.addWidget(title)

        # Section: Import from Excel
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Importing from Excel</h3>"
            "<p>The Import from Excel tool allows you to upload equipment records in bulk.</p>"
            "<ul>"
            "<li>Select an .xlsx file containing your equipment list.</li>"
            "<li>If multiple sheets are present, you will be prompted to choose one.</li>"
            "<li>The first row must contain column headers so the importer can match fields.</li>"
            "<li>Required columns include Area, Customer, BLDG, Room, Serial Number, Model, "
            "Contact, Contact Phone, IT Support, IT Phone, and Notes/Comments.</li>"
            "<li>Alternative header names such as 'Serial No' or 'Notes / Comments' are also accepted.</li>"
            "<li>Blank rows are automatically skipped during import.</li>"
            "<li>Unrecognized columns are ignored.</li>"
            "</ul>"
        )
        section1.setStyleSheet("color: #ddd;")
        section1.setWordWrap(True)
        layout.addWidget(section1)

        # Section: Filters & Columns
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Filtering and Column Visibility</h3>"
            "<p>The Filters button opens a panel that lets you narrow down records and control which columns are displayed.</p>"
            "<ul>"
            "<li>Each column has its own set of selectable values.</li>"
            "<li>You can hide or show any columns using the Visible Columns list.</li>"
            "<li>The Clear All Filters button resets all filters and restores full visibility.</li>"
            "<li>Filters remain active until you explicitly clear or modify them.</li>"
            "</ul>"
        )
        section2.setStyleSheet("color: #ddd;")
        section2.setWordWrap(True)
        layout.addWidget(section2)

        # Section: Sorting and Header Tools
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Sorting and Header Tools</h3>"
            "<p>Column headers support sorting and additional filtering shortcuts.</p>"
            "<ul>"
            "<li>Left-click a column header to sort the table by that column.</li>"
            "<li>Right-click a column header to open a filter popup for that specific column.</li>"
            "<li>If a column has a filter applied, a small indicator (⏷) appears in its header.</li>"
            "<li>Sorting and filtering can be used together.</li>"
            "</ul>"
        )
        section3.setStyleSheet("color: #ddd;")
        section3.setWordWrap(True)
        layout.addWidget(section3)

        # Close button
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

        # Force the dialog to scroll to the top
        self.ensurePolished()
        self.repaint()
        try:
            self.scroll(0, -99999)
        except:
            pass
