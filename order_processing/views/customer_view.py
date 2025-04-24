"""
Customer management view for the order processing application.
"""
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QGroupBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from ..controllers.application_controller import ApplicationController
from ..models.customer import Customer

class CustomerDialog(QDialog):
    """Dialog for adding or editing a customer."""
    
    def __init__(self, parent=None, customer: Optional[Customer] = None):
        """Initialize the customer dialog.
        
        Args:
            parent: Parent widget
            customer: Customer to edit, or None for a new customer
        """
        super().__init__(parent)
        
        self.customer = customer
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Add Customer" if not self.customer else "Edit Customer")
        self.setMinimumWidth(450)
        
        # Create form layout
        layout = QVBoxLayout(self)
        
        # Customer information section
        info_group = QGroupBox("Customer Information")
        info_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter customer name")
        if self.customer:
            self.name_input.setText(self.customer.name)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        if self.customer:
            self.phone_input.setText(self.customer.phone)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        if self.customer:
            self.email_input.setText(self.customer.email)
        
        info_layout.addRow("Name:", self.name_input)
        info_layout.addRow("Phone:", self.phone_input)
        info_layout.addRow("Email:", self.email_input)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Address section
        address_group = QGroupBox("Address")
        address_layout = QFormLayout()
        
        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Enter street address")
        if self.customer and self.customer.address:
            self.street_input.setText(self.customer.address.get("street", ""))
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city")
        if self.customer and self.customer.address:
            self.city_input.setText(self.customer.address.get("city", ""))
        
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("Enter state/province")
        if self.customer and self.customer.address:
            self.state_input.setText(self.customer.address.get("state", ""))
        
        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText("Enter postal/zip code")
        if self.customer and self.customer.address:
            self.zip_input.setText(self.customer.address.get("zip", ""))
        
        address_layout.addRow("Street:", self.street_input)
        address_layout.addRow("City:", self.city_input)
        address_layout.addRow("State/Province:", self.state_input)
        address_layout.addRow("Postal/ZIP Code:", self.zip_input)
        
        address_group.setLayout(address_layout)
        layout.addWidget(address_group)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_data(self) -> Dict[str, Any]:
        """Get the customer data from the form.
        
        Returns:
            Dictionary containing customer data
        """
        return {
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": {
                "street": self.street_input.text().strip(),
                "city": self.city_input.text().strip(),
                "state": self.state_input.text().strip(),
                "zip": self.zip_input.text().strip()
            }
        }


class CustomerView(QWidget):
    """View for managing customers."""
    
    # Signal emitted when a customer is selected
    customer_selected = pyqtSignal(Customer)
    
    def __init__(self, controller: ApplicationController):
        """Initialize the customer view.
        
        Args:
            controller: The application controller
        """
        super().__init__()
        
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create header
        header_layout = QHBoxLayout()
        title_label = QLabel("Customer Management")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers...")
        self.search_input.textChanged.connect(self.search_customers)
        header_layout.addWidget(self.search_input)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Create customer table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(5)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Address"])
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.itemDoubleClicked.connect(self.view_customer)
        
        # Set column widths
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        main_layout.addWidget(self.customer_table, 1)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Customer")
        self.add_button.clicked.connect(self.add_customer)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Customer")
        self.edit_button.clicked.connect(self.edit_customer)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Customer")
        self.delete_button.clicked.connect(self.delete_customer)
        button_layout.addWidget(self.delete_button)
        
        self.view_button = QPushButton("View Details")
        self.view_button.clicked.connect(self.view_customer)
        button_layout.addWidget(self.view_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Reload customer data from the database."""
        # Clear the table
        self.customer_table.setRowCount(0)
        
        # Get customers from controller
        customers = self.controller.get_all_customers()
        
        # Add customers to table
        for customer in customers:
            self.add_customer_to_table(customer)
    
    def add_customer_to_table(self, customer: Customer):
        """Add a customer to the table.
        
        Args:
            customer: The customer to add
        """
        row = self.customer_table.rowCount()
        self.customer_table.insertRow(row)
        
        # Set customer data
        self.customer_table.setItem(row, 0, QTableWidgetItem(str(customer.customer_id)))
        self.customer_table.setItem(row, 1, QTableWidgetItem(customer.name))
        self.customer_table.setItem(row, 2, QTableWidgetItem(customer.phone))
        self.customer_table.setItem(row, 3, QTableWidgetItem(customer.email))
        
        # Format address
        address_parts = []
        if customer.address:
            if customer.address.get("street"):
                address_parts.append(customer.address["street"])
            
            city_state = []
            if customer.address.get("city"):
                city_state.append(customer.address["city"])
            
            if customer.address.get("state"):
                city_state.append(customer.address["state"])
            
            if city_state:
                address_parts.append(", ".join(city_state))
            
            if customer.address.get("zip"):
                address_parts.append(customer.address["zip"])
        
        address_text = " ".join(address_parts) if address_parts else "No address provided"
        self.customer_table.setItem(row, 4, QTableWidgetItem(address_text))
    
    def search_customers(self):
        """Search for customers based on the search input."""
        query = self.search_input.text().strip()
        
        if not query:
            # If search is empty, show all customers
            self.refresh_data()
            return
        
        # Search for customers
        customers = self.controller.search_customers(query)
        
        # Clear the table
        self.customer_table.setRowCount(0)
        
        # Add matching customers to table
        for customer in customers:
            self.add_customer_to_table(customer)
    
    def add_customer(self):
        """Open dialog to add a new customer."""
        dialog = CustomerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            customer_data = dialog.get_data()
            
            # Validate required fields
            if not customer_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Customer name is required.")
                return
            
            # Add customer through controller
            success, customer, error = self.controller.add_customer(
                name=customer_data["name"],
                phone=customer_data["phone"],
                email=customer_data["email"],
                address=customer_data["address"]
            )
            
            if success and customer:
                self.add_customer_to_table(customer)
                QMessageBox.information(self, "Success", "Customer added successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to add customer: {error}")
    
    def edit_customer(self):
        """Open dialog to edit the selected customer."""
        # Get selected customer
        selected_rows = self.customer_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return
        
        # Get customer ID from the first column
        row = selected_rows[0].row()
        customer_id_item = self.customer_table.item(row, 0)
        if not customer_id_item:
            return
        
        customer_id = int(customer_id_item.text())
        
        # Find customer
        customer = self.controller.get_customer_by_id(customer_id)
        if not customer:
            QMessageBox.critical(self, "Error", "Customer not found.")
            return
        
        # Show edit dialog
        dialog = CustomerDialog(self, customer)
        if dialog.exec_() == QDialog.Accepted:
            customer_data = dialog.get_data()
            
            # Validate required fields
            if not customer_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Customer name is required.")
                return
            
            # Update customer through controller
            success, updated_customer, error = self.controller.update_customer(
                customer_id=customer_id,
                name=customer_data["name"],
                phone=customer_data["phone"],
                email=customer_data["email"],
                address=customer_data["address"]
            )
            
            if success and updated_customer:
                # Update table row
                self.customer_table.setItem(row, 1, QTableWidgetItem(updated_customer.name))
                self.customer_table.setItem(row, 2, QTableWidgetItem(updated_customer.phone))
                self.customer_table.setItem(row, 3, QTableWidgetItem(updated_customer.email))
                
                # Update address
                address_parts = []
                if updated_customer.address:
                    if updated_customer.address.get("street"):
                        address_parts.append(updated_customer.address["street"])
                    
                    city_state = []
                    if updated_customer.address.get("city"):
                        city_state.append(updated_customer.address["city"])
                    
                    if updated_customer.address.get("state"):
                        city_state.append(updated_customer.address["state"])
                    
                    if city_state:
                        address_parts.append(", ".join(city_state))
                    
                    if updated_customer.address.get("zip"):
                        address_parts.append(updated_customer.address["zip"])
                
                address_text = " ".join(address_parts) if address_parts else "No address provided"
                self.customer_table.setItem(row, 4, QTableWidgetItem(address_text))
                
                QMessageBox.information(self, "Success", "Customer updated successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to update customer: {error}")
    
    def delete_customer(self):
        """Delete the selected customer."""
        # Get selected customer
        selected_rows = self.customer_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return
        
        # Get customer ID from the first column
        row = selected_rows[0].row()
        customer_id_item = self.customer_table.item(row, 0)
        if not customer_id_item:
            return
        
        customer_id = int(customer_id_item.text())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this customer? This will also delete all associated orders.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delete customer through controller
        success, error = self.controller.delete_customer(customer_id)
        
        if success:
            # Remove from table
            self.customer_table.removeRow(row)
            QMessageBox.information(self, "Success", "Customer deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to delete customer: {error}")
    
    def view_customer(self):
        """View details of the selected customer."""
        # Get selected customer
        selected_rows = self.customer_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a customer to view.")
            return
        
        # Get customer ID from the first column
        row = selected_rows[0].row()
        customer_id_item = self.customer_table.item(row, 0)
        if not customer_id_item:
            return
        
        customer_id = int(customer_id_item.text())
        
        # Find customer
        customer = self.controller.get_customer_by_id(customer_id)
        if not customer:
            QMessageBox.critical(self, "Error", "Customer not found.")
            return
        
        # Emit the customer selected signal
        self.customer_selected.emit(customer)