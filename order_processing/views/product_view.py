"""
Product management view for the order processing application.
"""
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QGroupBox, QSplitter, QDoubleSpinBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from ..controllers.application_controller import ApplicationController
from ..models.product import Product

class ProductDialog(QDialog):
    """Dialog for adding or editing a product."""
    
    def __init__(self, parent=None, product: Optional[Product] = None):
        """Initialize the product dialog.
        
        Args:
            parent: Parent widget
            product: Product to edit, or None for a new product
        """
        super().__init__(parent)
        
        self.product = product
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Add Product" if not self.product else "Edit Product")
        self.setMinimumWidth(400)
        
        # Create form layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Product fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        if self.product:
            self.name_input.setText(self.product.name)
        
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Enter SKU (Stock Keeping Unit)")
        if self.product:
            self.sku_input.setText(self.product.sku)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter product description")
        if self.product:
            self.description_input.setText(self.product.description)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSingleStep(1.0)
        self.price_input.setPrefix("$")
        if self.product:
            self.price_input.setValue(self.product.price)
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 1000000)
        if self.product:
            self.stock_input.setValue(self.product.stock_quantity)
        
        # Add fields to form
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("SKU:", self.sku_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Price:", self.price_input)
        form_layout.addRow("Stock Quantity:", self.stock_input)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_data(self) -> Dict[str, Any]:
        """Get the product data from the form.
        
        Returns:
            Dictionary containing product data
        """
        return {
            "name": self.name_input.text().strip(),
            "sku": self.sku_input.text().strip(),
            "description": self.description_input.text().strip(),
            "price": self.price_input.value(),
            "stock_quantity": self.stock_input.value()
        }


class ProductView(QWidget):
    """View for managing products."""
    
    def __init__(self, controller: ApplicationController):
        """Initialize the product view.
        
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
        title_label = QLabel("Product Management")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.search_products)
        header_layout.addWidget(self.search_input)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Create product table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(["ID", "Name", "SKU", "Description", "Price", "Stock"])
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SingleSelection)
        self.product_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.product_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.product_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        main_layout.addWidget(self.product_table, 1)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Product")
        self.edit_button.clicked.connect(self.edit_product)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Product")
        self.delete_button.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_button)
        
        self.low_stock_button = QPushButton("Show Low Stock")
        self.low_stock_button.clicked.connect(self.show_low_stock)
        button_layout.addWidget(self.low_stock_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Reload product data from the database."""
        # Clear the table
        self.product_table.setRowCount(0)
        
        # Get products from controller
        products = self.controller.get_all_products()
        
        # Add products to table
        for product in products:
            self.add_product_to_table(product)
    
    def add_product_to_table(self, product: Product):
        """Add a product to the table.
        
        Args:
            product: The product to add
        """
        row = self.product_table.rowCount()
        self.product_table.insertRow(row)
        
        # Set product data
        self.product_table.setItem(row, 0, QTableWidgetItem(str(product.product_id)))
        self.product_table.setItem(row, 1, QTableWidgetItem(product.name))
        self.product_table.setItem(row, 2, QTableWidgetItem(product.sku))
        self.product_table.setItem(row, 3, QTableWidgetItem(product.description))
        
        # Format price with 2 decimal places and dollar sign
        price_item = QTableWidgetItem(f"${product.price:.2f}")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.product_table.setItem(row, 4, price_item)
        
        # Set stock quantity
        stock_item = QTableWidgetItem(str(product.stock_quantity))
        stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Highlight low stock items in red
        if product.stock_quantity < 10:
            stock_item.setForeground(Qt.red)
        
        self.product_table.setItem(row, 5, stock_item)
    
    def search_products(self):
        """Search for products based on the search input."""
        query = self.search_input.text().strip()
        
        if not query:
            # If search is empty, show all products
            self.refresh_data()
            return
        
        # Search for products
        products = self.controller.search_products(query)
        
        # Clear the table
        self.product_table.setRowCount(0)
        
        # Add matching products to table
        for product in products:
            self.add_product_to_table(product)
    
    def show_low_stock(self):
        """Show only products with low stock."""
        # Get low stock products (less than 10 items)
        products = self.controller.get_low_stock_products(10)
        
        # Clear the table
        self.product_table.setRowCount(0)
        
        # Add low stock products to table
        for product in products:
            self.add_product_to_table(product)
        
        # Show message if no low stock products
        if not products:
            QMessageBox.information(
                self,
                "Low Stock Products",
                "No products with low stock found."
            )
    
    def add_product(self):
        """Open dialog to add a new product."""
        dialog = ProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_data()
            
            # Validate required fields
            if not product_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Product name is required.")
                return
            
            if not product_data["sku"]:
                QMessageBox.warning(self, "Validation Error", "SKU is required.")
                return
            
            # Add product through controller
            success, product, error = self.controller.add_product(
                name=product_data["name"],
                sku=product_data["sku"],
                description=product_data["description"],
                price=product_data["price"],
                stock_quantity=product_data["stock_quantity"]
            )
            
            if success and product:
                self.add_product_to_table(product)
                QMessageBox.information(self, "Success", "Product added successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to add product: {error}")
    
    def edit_product(self):
        """Open dialog to edit the selected product."""
        # Get selected product
        selected_rows = self.product_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
        
        # Get product ID from the first column
        row = selected_rows[0].row()
        product_id_item = self.product_table.item(row, 0)
        if not product_id_item:
            return
        
        product_id = int(product_id_item.text())
        
        # Find product
        product = Product.find_by_id(product_id)
        if not product:
            QMessageBox.critical(self, "Error", "Product not found.")
            return
        
        # Show edit dialog
        dialog = ProductDialog(self, product)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_data()
            
            # Validate required fields
            if not product_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Product name is required.")
                return
            
            if not product_data["sku"]:
                QMessageBox.warning(self, "Validation Error", "SKU is required.")
                return
            
            # Update product through controller
            success, updated_product, error = self.controller.update_product(
                product_id=product_id,
                name=product_data["name"],
                sku=product_data["sku"],
                description=product_data["description"],
                price=product_data["price"],
                stock_quantity=product_data["stock_quantity"]
            )
            
            if success and updated_product:
                # Update table row
                self.product_table.setItem(row, 1, QTableWidgetItem(updated_product.name))
                self.product_table.setItem(row, 2, QTableWidgetItem(updated_product.sku))
                self.product_table.setItem(row, 3, QTableWidgetItem(updated_product.description))
                
                price_item = QTableWidgetItem(f"${updated_product.price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.product_table.setItem(row, 4, price_item)
                
                stock_item = QTableWidgetItem(str(updated_product.stock_quantity))
                stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if updated_product.stock_quantity < 10:
                    stock_item.setForeground(Qt.red)
                
                self.product_table.setItem(row, 5, stock_item)
                
                QMessageBox.information(self, "Success", "Product updated successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to update product: {error}")
    
    def delete_product(self):
        """Delete the selected product."""
        # Get selected product
        selected_rows = self.product_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        # Get product ID from the first column
        row = selected_rows[0].row()
        product_id_item = self.product_table.item(row, 0)
        if not product_id_item:
            return
        
        product_id = int(product_id_item.text())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delete product through controller
        success, error = self.controller.delete_product(product_id)
        
        if success:
            # Remove from table
            self.product_table.removeRow(row)
            QMessageBox.information(self, "Success", "Product deleted successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to delete product: {error}")