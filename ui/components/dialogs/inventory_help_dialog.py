from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog

"""
This module defines the InventoryHelpDialog-- a help window that helps users with key features of 
the Inventory page. It explains how to use the bulk 'Import from Excel' function, how to properly
use the 'sort' and 'filter' functions via right-click and drop-down menus, and how to change the
visibility of the individual columns.
"""

class InventoryHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Help – Inventory Page")
        self.resize(650, 520)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Using the Inventory Page")
        title.setStyleSheet("font: bold 20px 'Segoe UI'; color: #00ff99;")
        layout.addWidget(title)

        # Import from Excel Section
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Importing from Excel</h3>"
            "<p>The Import from Excel feature allows you to upload inventory items in bulk.</p>"
            "<ul>"
            "<li>Select an .xlsx file that contains your inventory list.</li>"
            "<li>If multiple sheets exist, you will be prompted to choose one.</li>"
            "<li>The first row must contain column headers so the importer can match each field.</li>"
            "<li>Common fields include Category, Subcategory, Brand, Model, Description, Warranty, "
            "PO Number, and Notes.</li>"
            "<li>Blank rows are skipped automatically.</li>"
            "<li>Unrecognized columns are ignored safely.</li>"
            "</ul>"
        )
        section1.setWordWrap(True)
        section1.setStyleSheet("color: #ddd;")
        layout.addWidget(section1)

        # Filters / Columns Section
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Filtering and Column Visibility</h3>"
            "<p>The Filters button opens a panel that lets you narrow down your inventory list "
            "and control which table columns are displayed.</p>"
            "<ul>"
            "<li>Each column displays all unique values found in your data.</li>"
            "<li>You can select any combination of these values to filter the table.</li>"
            "<li>You may hide or show specific columns using the Visible Columns list.</li>"
            "<li>Clear All Filters restores full visibility and removes all filters.</li>"
            "<li>Filters stay active until you clear or change them.</li>"
            "</ul>"
        )
        section2.setWordWrap(True)
        section2.setStyleSheet("color: #ddd;")
        layout.addWidget(section2)

        # Sorting / Header Tools
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Sorting and Header Tools</h3>"
            "<p>Table headers provide built-in sorting and quick filtering options.</p>"
            "<ul>"
            "<li>Left-click a header to sort by that column.</li>"
            "<li>Click again to reverse the sort direction.</li>"
            "<li>Right-click any header to open a filter popup for that specific column.</li>"
            "<li>Columns with active filters show a small ⏷ indicator in the header.</li>"
            "<li>Sorting and filtering work together and can be used simultaneously.</li>"
            "</ul>"
        )
        section3.setWordWrap(True)
        section3.setStyleSheet("color: #ddd;")
        layout.addWidget(section3)

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
