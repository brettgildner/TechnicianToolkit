from PySide6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,
                               QLabel,QFrame,QStackedWidget)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import os
from ui.pages.dashboard_page import DashboardPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.mileage_page import MileagePage
from ui.pages.parts_page import PartsPage
from ui.pages.service_activity_page import ServiceActivityPage
from ui.pages.equipment_info_page import EquipmentInfoPage
from ui.pages.expense_report_page import ExpenseReportPage
from ui.signals.model_signals import model_signals

"""
This page defines the primary app using QMainWindow, builds a left-aligned sidebar which 
is visible on all pages, and a 'page container' on the right using QStackedWidget. 
QStackedWidget uses a pages dictionary to map the pages to be shown to the pages which are 
defined in ui.pages. 

App.py page index:
class App(): Main window and page manager.
 - def __init__(): Build UI, load pages, wire signals.
 - def _create_sidebar(): builds the entire left navigation area
 - def show_page(): switches the 'active' page
 - def sign_out(): signs the user out
 - def enable_sidebar(): shows the sidebar and enables nav buttons
 - def disable_sidebar(): hides sidebar/disables nav buttons
 - def refresh_service_activity(): refreshes service activity for dashboard widget
 - def refresh_inventory(): refreshes inventory for dashboard widget
 - def refresh_mileage(): [not currently in use] refreshes mileage tracker
 - def refresh_parts(): [not currently in use] refreshes parts order page
"""

class App(QMainWindow):
    # Represents the application's main window, handling layout, navigation,
    # lazy page loading, and sidebar behavior.

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Technician Toolkit")
        self.resize(1200, 800)
        self.setMinimumSize(1050, 700)

        # Central layout > contains sidebar + page area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # HBox: Sidebar (left) | Pages (right)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar (left panel)
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # QStackedWidget is used to switch between different pages.
        self.container = QStackedWidget()
        main_layout.addWidget(self.container, 1)  # stretch factor = 1

        # Map page names to the corresponding page classes.
        self.pages = {
            "dashboard": DashboardPage,
            "inventory": InventoryPage,
            "mileage": MileagePage,
            "parts": PartsPage,
            "service_activity": ServiceActivityPage,
            "equipment_info": EquipmentInfoPage,
            "expense_report": ExpenseReportPage
        }

        # Stores instantiated page objects for lazy loading.
        self.page_instances = {}

        model_signals.inventory_changed.connect(self.refresh_inventory)
        model_signals.service_activity_changed.connect(self.refresh_service_activity)

        # Preload inventory page
        self.show_page("dashboard")
        self.show_page("inventory")
        self.container.setCurrentIndex(0)

        # Sidebar visibility state
        self.sidebar_enabled = False


    # Sidebar creation
    def _create_sidebar(self):
        # Creates the left sidebar containing the logo, navigation buttons, and sign-out button.
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                text-align: left;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #242424;
                color: #00ff99;
            }
            QLabel {
                color: #00cc88;
            }
        """)

        # Vertical layout inside sidebar
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Logo + title header
        header = QVBoxLayout()
        logo_path = os.path.join("assets", "icons", "logo.png")

        # Load the logo only if the file exists
        if os.path.exists(logo_path):
            logo = QLabel()
            # QPixmap loads images and `scaled()` resizes smoothly
            pixmap = QPixmap(logo_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            header.addWidget(logo)

        # App title text
        title = QLabel("Technician Toolkit")
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title)
        layout.addLayout(header)
        layout.addSpacing(10)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard", "dashboard.png"),
            ("Service Activity", "service_activity", "service.png"),
            ("Equipment Info", "equipment_info", "equipment.png"),
            ("Inventory", "inventory", "inventory.png"),
            ("Parts Ordering", "parts", "parts.png"),
            ("Expense Report", "expense_report", "expense.png"),
            ("Mileage Tracker", "mileage", "mileage.png"),
        ]

        for text, key, icon_file in nav_items:
            btn = QPushButton(f"  {text}")

            # Attach icon if file exists
            icon_path = os.path.join("assets", "icons", icon_file)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))

            # Clicking the button triggers page navigation
            btn.clicked.connect(lambda _, k=key: self.show_page(k))

            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        # Push remaining content to the top, leaving space before sign out
        layout.addStretch()

        # Sign-out button
        logout_btn = QPushButton("  Sign Out")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)

        # Clicking triggers sign_out() method
        logout_btn.clicked.connect(self.sign_out)
        layout.addWidget(logout_btn)
        return sidebar

    # Page navigation
    def show_page(self, name):
        # Switches the active page, creating pages on demand and wiring
        # cross-references as needed.

        # Lazy-create page only if it hasn’t been created before.
        if name not in self.page_instances:
            page_class = self.pages.get(name)

            if page_class is None:
                print(f"[App] No page named '{name}' found.")
                return

            # Create the page instance
            page = page_class(self.container, controller=self)
            self.page_instances[name] = page
            self.container.addWidget(page)

            # Register special pages as attributes for easy access
            if name == "inventory":
                self.inventory_page = page
            if name == "service_activity":
                self.service_activity_page = page

            # If InventoryPage was created now, wire ALL existing SA pages to it
            if isinstance(page, InventoryPage):
                for p in self.page_instances.values():
                    if isinstance(p, ServiceActivityPage):
                        p.inventory_page = page

            # If ServiceActivityPage was created now, wire it to any existing inventory page
            if isinstance(page, ServiceActivityPage):
                for p in self.page_instances.values():
                    if isinstance(p, InventoryPage):
                        page.inventory_page = p

        # Show page
        widget = self.page_instances[name]
        self.container.setCurrentWidget(widget)

    def sign_out(self):
        # Closes the app
        self.close()

    def enable_sidebar(self):
        # Shows the sidebar and enables navigation buttons.
        self.sidebar.setVisible(True)
        self.sidebar_enabled = True

        # Re-enable all navigation buttons
        for btn in self.nav_buttons.values():
            btn.setEnabled(True)

    def disable_sidebar(self):
        # Hides the sidebar and disables all navigation to prevent interaction.
        self.sidebar.setVisible(False)
        self.sidebar_enabled = False

        # Disable navigation buttons so they cannot be clicked
        for btn in self.nav_buttons.values():
            btn.setEnabled(False)

    # Refresh Methods
    def refresh_service_activity(self):
        if hasattr(self, "service_activity_page") and self.service_activity_page:
            self.service_activity_page.load_items()

    def refresh_inventory(self):
        if hasattr(self, "inventory_page") and self.inventory_page:
            self.inventory_page.load_items()

    # Used for a previous version of the app which contained widgets that showed
    # recent mileage; Not currently in use
    def refresh_mileage(self):
        if hasattr(self, "mileage_page") and self.mileage_page:
            self.mileage_page.load_items()

    # Used for a previous version of the app which contained widgets that showed
    # parts listed on the 'parts order' page; Not currently in use
    def refresh_parts(self):
        if hasattr(self, "parts_page") and self.parts_page:
            self.parts_page.load_items()
