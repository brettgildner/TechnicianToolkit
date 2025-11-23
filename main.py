import sys
from PySide6.QtWidgets import QApplication
from core.logic import init_user_table, init_all_tables
from ui.pages.login_page import LoginPage

"""
This is the entry point of the application and runs when the program starts. It initializes the 
database, sets up Qt, shows the login screen, and launches the main window after login.
"""

# Launches the main application window after a successful login.
# Imported lazily to avoid circular dependencies during startup.
def launch_main_window():
    from app import App
    win = App()
    win.show()

# The following code runs only when this file is executed directly.
if __name__ == "__main__":
    # Prepare the database by creating any required tables.
    init_all_tables()
    init_user_table()

    # Create the QApplication object, which is required for all Qt GUI applications.
    app = QApplication(sys.argv)

    # Show the login screen, which triggers launch_main_window() when login succeeds.
    login = LoginPage(on_login_success=launch_main_window)
    login.show()

    # Start Qt's event loop and exit cleanly once all windows close.
    sys.exit(app.exec())
