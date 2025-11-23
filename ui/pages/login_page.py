from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from core.logic import login_user
from ui.pages.signup_page import SignupPage

"""
This page implements the Login Page UI, providing a centered, styled form where users can enter their 
username and password to authenticate. It builds a clean card-style login box with input fields, a 
login button that triggers backend authentication, and a “Create Account” button that opens the SignupPage 
inside a modal dialog. The page manages user feedback for missing credentials or failed logins, and calls 
a success callback when authentication completes, allowing the application to transition to the main 
interface.

ui.pages.login_page.py index:
class LoginPage(): Login screen UI.
 - def __init__(): Build login form UI.
 - def try_login(): Attempt user authentication.
 - def open_signup(): Open account-creation dialog.
"""

class LoginPage(QWidget):
    def __init__(self, parent=None, on_login_success=None):
        super().__init__(parent)

        # This function (if provided) will be called after a successful login.
        # The main window provides this so the app knows what to do next.
        self.on_login_success = on_login_success

        # Main layout (top-level vertical layout for the whole page)
        outer_layout = QVBoxLayout(self)
        # Remove margins so the content takes up the full window width/height.
        outer_layout.setContentsMargins(0, 0, 0, 0)
        # Remove spacing between stacked elements.
        outer_layout.setSpacing(0)

        # A simple container that holds the login form
        container = QWidget()
        form_layout = QVBoxLayout(container)
        # Center the login box vertically
        form_layout.setAlignment(Qt.AlignCenter)

        # Add space above the form, then the form, then space below
        outer_layout.addStretch()
        outer_layout.addWidget(container, alignment=Qt.AlignCenter)
        outer_layout.addStretch()

        # Login form box (visual card-style box)
        form_box = QWidget()
        # Styling that controls login form visuals: dark background, rounded corners, padding, etc.
        form_box.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                border-radius: 10px;
                padding: 40px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: #0077cc;
                color: white;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)

        # Layout inside the form box
        form = QVBoxLayout(form_box)
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(12)

        # Title label
        title = QLabel("Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: bold 26px 'Segoe UI';")
        form.addWidget(title)

        # Username field
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Username")
        form.addWidget(self.username_entry)

        # Password field
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Password")
        # This hides the text behind dot • characters
        self.password_entry.setEchoMode(QLineEdit.Password)
        form.addWidget(self.password_entry)

        # Login button
        login_btn = QPushButton("Login")
        # When clicked, attempt to authenticate the user
        login_btn.clicked.connect(self.try_login)
        form.addWidget(login_btn)

        # Create account button
        create_btn = QPushButton("Create Account")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #dddddd;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        # Opens the sign-up dialog
        create_btn.clicked.connect(self.open_signup)
        form.addWidget(create_btn)

        # Add the entire form box to the centered container
        form_layout.addWidget(form_box, alignment=Qt.AlignCenter)

    # Login attempt logic
    def try_login(self):
        # Retrieve values the user typed in
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        # If either box is empty, warn the user
        if not username or not password:
            QMessageBox.warning(
                self, "Missing Info",
                "Please enter both username and password."
            )
            return

        # login_user() is the backend logic that checks the database
        if login_user(username, password):

            # If login is successful, call the callback (main window handler)
            if self.on_login_success:
                self.on_login_success()

            # Close the login window afterwards
            self.close()

        else:
            # If login failed, show an error pop-up
            QMessageBox.critical(
                self, "Login Failed",
                "Invalid username or password."
            )

    # Open sign-up page in popup dialog
    def open_signup(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout

        # Hide the login window while the signup dialog is open
        self.hide()

        # A dialog window for sign-up
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Account")
        dialog.setModal(True)  # prevents interacting with login until closed

        # (Internal flag—used by SignupPage if needed)
        dialog._closed_from_back_button = False

        layout = QVBoxLayout(dialog)

        # Create the SignupPage and embed it inside the dialog
        signup_page = SignupPage(parent=dialog, controller=None)
        signup_page.dialog_ref = dialog  # allows signup page to close the dialog
        layout.addWidget(signup_page)

        dialog.setMinimumWidth(400)

        # Open the dialog (blocks until closed)
        dialog.exec()

        # Show login window again after the dialog closes
        self.show()
