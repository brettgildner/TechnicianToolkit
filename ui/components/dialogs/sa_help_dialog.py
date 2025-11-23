from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog

"""
This module defines the ServiceActivityHelpDialog-- a help window that helps users with navigating 
the Service Activity page. It explains how to use the bulk 'Import from Excel' function in order to
migrate any pre-existing service activity logs, how to use the 'sort' and 'filter' functions via 
right-click and drop-down menus, and how to change the visibility of the individual columns.
"""

class ServiceActivityHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help – Service Activity Page")
        self.resize(650, 520)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Using the Service Activity Page")
        title.setStyleSheet("font: bold 20px 'Segoe UI'; color: #00ff99;")
        layout.addWidget(title)

        # Import from Excel Section
        section1 = QLabel(
            "<h3 style='color:#00ff99;'>Importing from Excel</h3>"
            "<p>This feature allows you to upload multiple service activity entries "
            "at once from an Excel file.</p>"
            "<ul>"
            "<li>Select an .xlsx file from your computer.</li>"
            "<li>If the workbook has multiple sheets, you will be prompted to choose one.</li>"
            "<li>The first row must contain header names so the importer can correctly map columns.</li>"
            "<li>If a header is missing, an error message will tell you which ones are required.</li>"
            "<li>Blank rows are skipped automatically.</li>"
            "<li>If the Call Duration is missing, it is calculated automatically from arrival/departure times.</li>"
            "</ul>"
        )
        section1.setWordWrap(True)
        section1.setStyleSheet("color: #ddd;")
        layout.addWidget(section1)

        # Filters & Columns Section
        section2 = QLabel(
            "<h3 style='color:#00ff99;'>Filters and Column Visibility</h3>"
            "<p>The Filters button opens a panel where you can filter data and control "
            "which columns are visible.</p>"
            "<ul>"
            "<li>Each column can be filtered independently using checkboxes.</li>"
            "<li>The 'Visible Columns' list allows hiding or showing columns.</li>"
            "<li>Use 'Clear All Filters' to reset everything instantly.</li>"
            "<li>Filters remain active until removed manually.</li>"
            "</ul>"
        )
        section2.setWordWrap(True)
        section2.setStyleSheet("color: #ddd;")
        layout.addWidget(section2)

        # Sorting & Header Tools
        section3 = QLabel(
            "<h3 style='color:#00ff99;'>Sorting and Header Tools</h3>"
            "<p>Your table supports full sorting and contextual header filtering.</p>"
            "<ul>"
            "<li>Left-click a column header to sort by that field.</li>"
            "<li>Click again to reverse the sort direction.</li>"
            "<li>Right-click a header to open a filter popup for that specific column.</li>"
            "<li>A ⏷ indicator appears when a column has an active filter.</li>"
            "<li>Sorting and filtering work together seamlessly.</li>"
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
