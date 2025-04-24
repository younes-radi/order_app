"""
Login view for the order processing application.
"""
from typing import Callable, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox,
    QDialog, QDialogButtonBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from ..controllers.application_controller import ApplicationController
from ..models.user import User

class LoginView(QDialog):
    """Login dialog for the order processing application."""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(User)
    
    def __init__(self, controller: ApplicationController, parent=None):
        """Initialize the login view.
        
        Args:
            controller: The application controller
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Order Processing - Login")
        self.setMinimumWidth(350)
        self.setMinimumHeight(200)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add logo/header
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        # Placeholder for logo - would be replaced with actual logo
        # logo_label.setPixmap(QPixmap("path/to/logo.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        
        title_label = QLabel("Order Processing System")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label, 1)
        
        layout.addLayout(header_layout)
        
        # Add separator
        separator = QLabel()
        separator.setFrameShape(QLabel.HLine)
        separator.setFrameShadow(QLabel.Sunken)
        layout.addWidget(separator)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.attempt_login)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Exit")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def attempt_login(self):
        """Attempt to log in with the entered credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            QMessageBox.warning(self, "Login Error", "Username is required.")
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Login Error", "Password is required.")
            self.password_input.setFocus()
            return
        
        # Try to log in
        success, user, error = self.controller.login(username, password)
        
        if success and user:
            # Emit the login successful signal
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", error or "Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()
            
    def set_defaults(self, username: str = "", password: str = ""):
        """Set default values for the login form (useful for development).
        
        Args:
            username: Default username
            password: Default password
        """
        self.username_input.setText(username)
        self.password_input.setText(password)


class CreateAdminDialog(QDialog):
    """Dialog for creating the initial admin user."""
    
    def __init__(self, controller: ApplicationController, parent=None):
        """Initialize the create admin dialog.
        
        Args:
            controller: The application controller
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Create Administrator Account")
        self.setMinimumWidth(400)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add info label
        info_label = QLabel(
            "No users were found in the system. Please create an administrator account to continue."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Admin form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_admin)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_admin(self):
        """Create the admin user with the entered information."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate input
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            self.password_input.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return
        
        # Create admin role if it doesn't exist
        success, admin_role, error = self.controller.get_or_create_role("Admin")
        
        if not success or not admin_role:
            QMessageBox.critical(self, "Error", f"Failed to create admin role: {error}")
            return
        
        # Create admin user
        success, user, error = self.controller.create_user(
            username=username,
            password=password,
            role_id=admin_role.role_id
        )
        
        if success and user:
            QMessageBox.information(
                self,
                "Success",
                f"Administrator account '{username}' has been created successfully."
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"Failed to create administrator account: {error}")