from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from core.logic import register_user

"""
This page defines the SignupPage, a form that allows users to create new accounts either as a popup 
launched from the LoginPage or as a full page within the main application. It builds a styled, centered 
signup interface with fields for username, email, and password, plus Sign Up and Back to Login buttons. 
The page handles validation, calls backend logic to register the user, displays success or error messages, 
and then either closes the popup or navigates back to the login page depending on how it was opened.

ui.pages.signup_page.py index:

class SignupPage(): Signup UI for creating accounts.
 - def __init__(): Set mode + build UI.
 - def _build_ui(): Construct signup form layout.
 - def try_signup(): Validate inputs and register user.
 - def back_to_login(): Return to login screen.
"""

class SignupPage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.is_popup = controller is None
        self.parent_login_window = parent if self.is_popup else None
        self.controller = controller
        self.on_signup = (
            lambda: controller.show_page("login")
            if controller else
            None
        )
        self._build_ui()

    def _build_ui(self):
        # Builds the full signup interface, including form fields and navigation buttons.

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 40)
        layout.setAlignment(Qt.AlignCenter)

        form_box = QWidget()
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
                selection-background-color: #0077cc;
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

        # Inner layout for the signup fields
        form = QVBoxLayout(form_box)
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(12)

        # Header title
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: bold 26px 'Segoe UI'; margin-bottom: 10px;")
        form.addWidget(title)

        # Username field
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Username")
        self.username_entry.setClearButtonEnabled(True)
        form.addWidget(self.username_entry)

        # Email field
        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("Email")
        self.email_entry.setClearButtonEnabled(True)
        form.addWidget(self.email_entry)

        # Password field
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setClearButtonEnabled(True)
        form.addWidget(self.password_entry)

        # Automatically focus the username field to speed up user flow
        self.username_entry.setFocus()

        # Signup button
        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.try_signup)
        signup_btn.setDefault(True)
        form.addWidget(signup_btn)

        # Back button
        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet("""
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

        # Back button behaves differently depending on popup/full-page mode.
        back_btn.clicked.connect(self.back_to_login)
        form.addWidget(back_btn)

        # Add the form_box to the main layout, centered
        layout.addWidget(form_box, alignment=Qt.AlignCenter)

    # Signup logic
    def try_signup(self):
        # Validate the form, attempt to register the user, and return to login depending on mode.
        username = self.username_entry.text().strip()
        email = self.email_entry.text().strip()
        password = self.password_entry.text().strip()

        # Basic validation
        if not username or not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return

        try:
            # Attempt to register the user using the application's logic layer
            if register_user(username, email, password):
                QMessageBox.information(
                    self, "Account Created",
                    "Your account was created successfully."
                )

                # In full-app mode, on_signup switches the QStackedWidget back to login page.
                # In popup mode, on_signup does nothing and the popup is closed separately.
                if self.on_signup:
                    self.on_signup()

                # If popup, close the dialog ourselves.
                if self.is_popup and self.parent_login_window:
                    # The popup parent is a QDialog created by LoginPage.
                    self.parent_login_window.done(0)

            else:
                QMessageBox.warning(
                    self, "Signup Failed",
                    "Unable to create account. Please try again."
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An unexpected error occurred:\n{e}"
            )

    # Return to login handler
    def back_to_login(self):
        # Returns the user to the login screen, either by closing the popup or switching pages.

        # Case 1: open inside a modal dialog (LoginPage > dialog > this page)
        if self.is_popup and self.parent_login_window:
            self.parent_login_window.done(0)
            return

        # Case 2: inside main application with a controller
        if self.controller and hasattr(self.controller, "show_page"):
            self.controller.show_page("login")
