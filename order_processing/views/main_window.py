"""
Main window implementation for the order processing application.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QAction, QStatusBar,
    QDialog, QLineEdit, QFormLayout, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import os

from order_processing.controllers.application_controller import ApplicationController

class LoginDialog(QDialog):
    """Dialog for user login."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.resize(300, 150)
        
        # Create form layout
        layout = QFormLayout()
        
        # Create input fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Add fields to layout
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        
        # Create buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        
        # Connect buttons
        self.login_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons to layout
        layout.addRow("", button_layout)
        
        self.setLayout(layout)

class OrderDialog(QDialog):
    """Dialog for creating a new order."""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.order_items = []
        self.total_cost = 0.0
        
        self.setWindowTitle("New Order")
        self.resize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Customer selection
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer:"))
        
        self.customer_combo = QComboBox()
        self.populate_customers()
        customer_layout.addWidget(self.customer_combo, 1)
        
        layout.addLayout(customer_layout)
        
        # Products section
        layout.addWidget(QLabel("Add Products:"))
        
        # Product selection
        product_layout = QHBoxLayout()
        
        product_layout.addWidget(QLabel("Product:"))
        self.product_combo = QComboBox()
        self.populate_products()
        product_layout.addWidget(self.product_combo, 2)
        
        product_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        product_layout.addWidget(self.quantity_spin)
        
        self.add_product_button = QPushButton("Add")
        self.add_product_button.clicked.connect(self.add_product_to_order)
        product_layout.addWidget(self.add_product_button)
        
        layout.addLayout(product_layout)
        
        # Order items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "SKU", "Quantity", "Price", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.items_table)
        
        # Remove selected item button
        remove_button = QPushButton("Remove Selected Item")
        remove_button.clicked.connect(self.remove_selected_item)
        layout.addWidget(remove_button)
        
        # Total cost
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Total Cost:"))
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        # Payment section
        payment_group_layout = QVBoxLayout()
        payment_group_layout.addWidget(QLabel("Payment:"))
        
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Amount:"))
        self.payment_amount = QDoubleSpinBox()
        self.payment_amount.setMinimum(0.01)
        self.payment_amount.setMaximum(9999.99)
        self.payment_amount.setPrefix("$")
        payment_layout.addWidget(self.payment_amount)
        
        payment_layout.addWidget(QLabel("Type:"))
        self.payment_type = QComboBox()
        self.payment_type.addItems(["Cash", "Credit Card", "Store Credit"])
        payment_layout.addWidget(self.payment_type)
        
        payment_group_layout.addLayout(payment_layout)
        
        # Reference number (for credit card)
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Reference Number:"))
        self.reference_input = QLineEdit()
        ref_layout.addWidget(self.reference_input)
        payment_group_layout.addLayout(ref_layout)
        
        layout.addLayout(payment_group_layout)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Order")
        self.create_button.clicked.connect(self.create_order)
        self.create_button.setEnabled(False)  # Disabled until customer and items added
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.payment_type.currentTextChanged.connect(self.on_payment_type_changed)
        self.on_payment_type_changed(self.payment_type.currentText())
    
    def populate_customers(self):
        """Populate the customers dropdown."""
        customers = self.controller.get_all_customers()
        for customer in customers:
            self.customer_combo.addItem(customer.name, customer.customer_id)
    
    def populate_products(self):
        """Populate the products dropdown."""
        products = self.controller.get_all_products()
        for product in products:
            if product.stock_quantity > 0:
                self.product_combo.addItem(f"{product.name} (${product.price:.2f})", product.product_id)
    
    def add_product_to_order(self):
        """Add a product to the order."""
        if self.product_combo.count() == 0:
            QMessageBox.warning(self, "No Products", "No products available to add.")
            return
            
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        
        product = None
        for p in self.controller.get_all_products():
            if p.product_id == product_id:
                product = p
                break
        
        if not product:
            QMessageBox.warning(self, "Error", "Selected product not found.")
            return
        
        if product.stock_quantity < quantity:
            QMessageBox.warning(self, "Insufficient Stock", 
                               f"Not enough stock available. Only {product.stock_quantity} units in stock.")
            return
        
        # Check if product already in order
        for i, item in enumerate(self.order_items):
            if item['product_id'] == product_id:
                # Update quantity if already in order
                new_quantity = item['quantity'] + quantity
                if product.stock_quantity < new_quantity:
                    QMessageBox.warning(self, "Insufficient Stock", 
                                       f"Not enough stock available. Only {product.stock_quantity} units in stock.")
                    return
                
                self.order_items[i]['quantity'] = new_quantity
                self.order_items[i]['total'] = new_quantity * product.price
                self.update_items_table()
                self.update_total()
                return
        
        # Add new product to order
        item = {
            'product_id': product_id,
            'product_name': product.name,
            'sku': product.sku,
            'quantity': quantity,
            'price': product.price,
            'total': quantity * product.price
        }
        self.order_items.append(item)
        self.update_items_table()
        self.update_total()
        self.create_button.setEnabled(len(self.order_items) > 0)
    
    def update_items_table(self):
        """Update the order items table."""
        self.items_table.setRowCount(len(self.order_items))
        
        for row, item in enumerate(self.order_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(item['sku']))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"${item['price']:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"${item['total']:.2f}"))
    
    def update_total(self):
        """Update the total cost label."""
        self.total_cost = sum(item['total'] for item in self.order_items)
        self.total_label.setText(f"${self.total_cost:.2f}")
        self.payment_amount.setValue(self.total_cost)
        self.payment_amount.setMinimum(self.total_cost)
    
    def remove_selected_item(self):
        """Remove the selected item from the order."""
        selected_rows = self.items_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove.")
            return
        
        row = selected_rows[0].row()
        if 0 <= row < len(self.order_items):
            self.order_items.pop(row)
            self.update_items_table()
            self.update_total()
            self.create_button.setEnabled(len(self.order_items) > 0)
    
    def on_payment_type_changed(self, payment_type):
        """Handle payment type change."""
        # Enable reference number input only for credit card payments
        if payment_type == "Credit Card":
            self.reference_input.setEnabled(True)
            self.reference_input.setPlaceholderText("Required for credit card")
        else:
            self.reference_input.setEnabled(False)
            self.reference_input.setText("")
            self.reference_input.setPlaceholderText("Not needed")
    
    def create_order(self):
        """Create a new order with the selected items."""
        if not self.order_items:
            QMessageBox.warning(self, "Empty Order", "Please add at least one product to the order.")
            return
        
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "No Customer", "Please select a customer for the order.")
            return
        
        # Create the order
        success, order, error = self.controller.create_order(customer_id)
        if not success:
            QMessageBox.critical(self, "Error", f"Failed to create order: {error}")
            return
        
        # Add items to the order
        for item in self.order_items:
            success, _, error = self.controller.add_order_item(item['product_id'], item['quantity'])
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to add item: {error}")
                # Cancel the order
                self.controller.cancel_order()
                return
        
        # Process payment
        payment_amount = self.payment_amount.value()
        payment_type_text = self.payment_type.currentText()
        
        # Map payment type text to values expected by the controller
        payment_type_map = {
            "Cash": "cash",
            "Credit Card": "credit_card",
            "Store Credit": "store_credit"
        }
        payment_type = payment_type_map.get(payment_type_text, "cash")
        
        reference_number = self.reference_input.text()
        
        # Validate reference number for credit card payments
        if payment_type == "credit_card" and not reference_number:
            QMessageBox.warning(self, "Missing Reference", "Reference number is required for credit card payments.")
            return
        
        # Process the payment
        success, payment, error = self.controller.process_payment(payment_amount, payment_type, reference_number)
        if not success:
            QMessageBox.critical(self, "Payment Error", f"Failed to process payment: {error}")
            # Cancel the order
            self.controller.cancel_order()
            return
        
        QMessageBox.information(self, "Success", "Order created and payment processed successfully!")
        self.accept()

class OrdersTab(QWidget):
    """Tab for managing orders."""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the orders tab UI."""
        layout = QVBoxLayout(self)
        
        # Add filter controls
        filter_layout = QHBoxLayout()
        
        # Status filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("All", None)
        self.status_combo.addItem("Draft", "draft")
        self.status_combo.addItem("Completed", "completed")
        self.status_combo.addItem("Cancelled", "cancelled")
        self.status_combo.currentIndexChanged.connect(self.refresh_orders)
        filter_layout.addWidget(self.status_combo)
        
        # Date range filter
        filter_layout.addWidget(QLabel("Date From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        # Search by customer
        filter_layout.addWidget(QLabel("Customer:"))
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Search by customer name")
        filter_layout.addWidget(self.customer_search)
        
        # Apply filters button
        self.apply_filter_btn = QPushButton("Apply Filters")
        self.apply_filter_btn.clicked.connect(self.refresh_orders)
        filter_layout.addWidget(self.apply_filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Date", "Status", "Total", "Actions"])
        self.orders_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.doubleClicked.connect(self.view_order_details)
        layout.addWidget(self.orders_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_orders)
        buttons_layout.addWidget(refresh_btn)
        
        # New order button
        new_order_btn = QPushButton("New Order")
        new_order_btn.clicked.connect(self.create_new_order)
        buttons_layout.addWidget(new_order_btn)
        
        # View details button
        view_details_btn = QPushButton("View Details")
        view_details_btn.clicked.connect(self.view_order_details)
        buttons_layout.addWidget(view_details_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial load of orders
        self.refresh_orders()
    
    def refresh_orders(self):
        """Refresh the orders table with filtered data."""
        self.orders_table.setRowCount(0)
        
        # Get filter values
        status = self.status_combo.currentData()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        customer_search = self.customer_search.text().strip()
        
        # Get all orders
        orders = []
        
        # Apply status filter if selected
        if status:
            orders = self.controller.get_orders_by_status(status)
        else:
            # Get by date range
            from datetime import datetime
            date_from_dt = datetime.combine(date_from, datetime.min.time())
            date_to_dt = datetime.combine(date_to, datetime.max.time())
            orders = self.controller.get_orders_by_date_range(date_from_dt, date_to_dt)
        
        # Filter by customer if search text provided
        if customer_search and orders:
            filtered_orders = []
            for order in orders:
                customer = self.controller.get_customer(order.customer_id)
                if customer and customer_search.lower() in customer.name.lower():
                    filtered_orders.append(order)
            orders = filtered_orders
        
        # Populate table
        for i, order in enumerate(orders):
            self.orders_table.insertRow(i)
            
            # Get customer name
            customer = self.controller.get_customer(order.customer_id)
            customer_name = customer.name if customer else "Unknown"
            
            # Format date
            order_date = order.order_date.strftime("%Y-%m-%d %H:%M") if order.order_date else "N/A"
            
            # Set order data
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(order.order_id)))
            self.orders_table.setItem(i, 1, QTableWidgetItem(customer_name))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order_date))
            self.orders_table.setItem(i, 3, QTableWidgetItem(order.status.capitalize()))
            self.orders_table.setItem(i, 4, QTableWidgetItem(f"${order.total_cost:.2f}"))
            
            # Add view button
            view_btn = QPushButton("View")
            view_btn.setProperty("order_id", order.order_id)
            view_btn.clicked.connect(lambda checked, order_id=order.order_id: self.view_order_detail(order_id))
            self.orders_table.setCellWidget(i, 5, view_btn)
    
    def create_new_order(self):
        """Create a new order."""
        dialog = OrderDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_orders()
    
    def view_order_details(self):
        """View details of the selected order."""
        selected_items = self.orders_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an order to view.")
            return
        
        # Get the order ID from the first column
        order_id = int(self.orders_table.item(selected_items[0].row(), 0).text())
        self.view_order_detail(order_id)
    
    def view_order_detail(self, order_id):
        """View details of a specific order."""
        dialog = OrderDetailDialog(self.controller, order_id, self)
        dialog.exec_()


class OrderDetailDialog(QDialog):
    """Dialog for viewing order details."""
    
    def __init__(self, controller, order_id, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.order_id = order_id
        
        self.setWindowTitle(f"Order Details - Order #{order_id}")
        self.resize(700, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Get order details
        order = self.controller.get_order(self.order_id)
        if not order:
            layout.addWidget(QLabel("Order not found."))
            self.setLayout(layout)
            return
        
        # Get customer details
        customer = self.controller.get_customer(order.customer_id)
        customer_name = customer.name if customer else "Unknown"
        
        # Order information section
        info_group = QGroupBox("Order Information")
        info_layout = QFormLayout()
        
        # Order details
        info_layout.addRow("Order ID:", QLabel(f"#{order.order_id}"))
        info_layout.addRow("Customer:", QLabel(customer_name))
        info_layout.addRow("Date:", QLabel(order.order_date.strftime("%Y-%m-%d %H:%M") if order.order_date else "N/A"))
        info_layout.addRow("Status:", QLabel(order.status.capitalize()))
        info_layout.addRow("Total:", QLabel(f"${order.total_cost:.2f}"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Order items section
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout()
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "SKU", "Quantity", "Price", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Get order items
        items = order.get_items()
        
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            # Get product details
            product = self.controller.get_product(item.product_id)
            product_name = product.name if product else "Unknown"
            sku = product.sku if product else "N/A"
            
            # Set item data
            self.items_table.setItem(i, 0, QTableWidgetItem(product_name))
            self.items_table.setItem(i, 1, QTableWidgetItem(sku))
            self.items_table.setItem(i, 2, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"${item.unit_price:.2f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"${item.quantity * item.unit_price:.2f}"))
        
        items_layout.addWidget(self.items_table)
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Payment information section
        payment_group = QGroupBox("Payment Information")
        payment_layout = QVBoxLayout()
        
        # Get payment details
        from order_processing.models.payment import Payment
        payments = Payment.find_by_order_id(order.order_id)
        
        if payments:
            payment_table = QTableWidget()
            payment_table.setColumnCount(5)
            payment_table.setHorizontalHeaderLabels(["Payment ID", "Date", "Amount", "Type", "Reference"])
            payment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            payment_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
            payment_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            payment_table.setRowCount(len(payments))
            for i, payment in enumerate(payments):
                payment_date = payment.payment_date.strftime("%Y-%m-%d %H:%M") if payment.payment_date else "N/A"
                
                payment_table.setItem(i, 0, QTableWidgetItem(str(payment.payment_id)))
                payment_table.setItem(i, 1, QTableWidgetItem(payment_date))
                payment_table.setItem(i, 2, QTableWidgetItem(f"${payment.amount:.2f}"))
                payment_table.setItem(i, 3, QTableWidgetItem(payment.payment_type.capitalize()))
                payment_table.setItem(i, 4, QTableWidgetItem(payment.reference_number or "N/A"))
            
            payment_layout.addWidget(payment_table)
        else:
            payment_layout.addWidget(QLabel("No payment information available."))
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        # Add print button
        print_btn = QPushButton("Print Receipt")
        print_btn.clicked.connect(lambda: self.print_receipt(order, customer, items, payments))
        buttons_layout.addWidget(print_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def print_receipt(self, order, customer, items, payments):
        """Print or save order receipt."""
        # In a real app, this would connect to a printer or generate a PDF
        # For now, we'll just show a message with the receipt content
        
        receipt = f"ORDER RECEIPT\n\n"
        receipt += f"Order #: {order.order_id}\n"
        receipt += f"Date: {order.order_date.strftime('%Y-%m-%d %H:%M')}\n"
        receipt += f"Customer: {customer.name if customer else 'Unknown'}\n\n"
        
        receipt += "ITEMS:\n"
        receipt += "-" * 50 + "\n"
        receipt += f"{'Product':<30}{'Qty':<5}{'Price':<8}{'Total':<10}\n"
        receipt += "-" * 50 + "\n"
        
        for item in items:
            product = self.controller.get_product(item.product_id)
            product_name = product.name if product else "Unknown"
            receipt += f"{product_name:<30}{item.quantity:<5}${item.unit_price:<7.2f}${item.quantity * item.unit_price:<9.2f}\n"
        
        receipt += "-" * 50 + "\n"
        receipt += f"{'TOTAL:':<43}${order.total_cost:.2f}\n\n"
        
        if payments:
            receipt += "PAYMENT:\n"
            for payment in payments:
                receipt += f"Amount: ${payment.amount:.2f}\n"
                receipt += f"Method: {payment.payment_type.capitalize()}\n"
                if payment.reference_number:
                    receipt += f"Reference: {payment.reference_number}\n"
        
        receipt += "\nThank you for your purchase!"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Order Receipt")
        msg.setText("Receipt Preview:")
        msg.setDetailedText(receipt)
        msg.exec_()

class MainWindow(QMainWindow):
    """Main window for the order processing application."""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
        # Show login dialog
        self.show_login_dialog()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("Order Processing Application")
        self.setMinimumSize(800, 600)
        
        # Create menu bar
        self.create_menus()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs (these will be implemented in more detail in separate files)
        self.create_dashboard_tab()
        self.create_customers_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_reports_tab()
        
        # Initially disable tabs until login
        self.tab_widget.setEnabled(False)
    
    def create_menus(self):
        """Create application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New order action
        new_order_action = QAction("New &Order", self)
        new_order_action.setShortcut("Ctrl+N")
        new_order_action.triggered.connect(self.create_new_order)
        file_menu.addAction(new_order_action)
        
        file_menu.addSeparator()
        
        # Backup action
        backup_action = QAction("&Backup Data", self)
        backup_action.triggered.connect(self.backup_data)
        file_menu.addAction(backup_action)
        
        # Restore action
        restore_action = QAction("&Restore Data", self)
        restore_action.triggered.connect(self.restore_data)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # User menu
        user_menu = self.menuBar().addMenu("&User")
        
        # Login action
        self.login_action = QAction("&Login", self)
        self.login_action.triggered.connect(self.show_login_dialog)
        user_menu.addAction(self.login_action)
        
        # Logout action
        self.logout_action = QAction("Log&out", self)
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        user_menu.addAction(self.logout_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_tab = QWidget()
        self.tab_widget.addTab(dashboard_tab, "Dashboard")
        
        # Implement dashboard UI
        layout = QVBoxLayout(dashboard_tab)
        
        # Welcome label
        welcome_label = QLabel("Welcome to the Order Processing Application")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # User info label
        self.user_info_label = QLabel("Not logged in")
        self.user_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.user_info_label)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        # New order button
        new_order_button = QPushButton("New Order")
        new_order_button.clicked.connect(self.create_new_order)
        actions_layout.addWidget(new_order_button)
        
        # Manage customers button
        customers_button = QPushButton("Manage Customers")
        customers_button.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))
        actions_layout.addWidget(customers_button)
        
        # Manage products button
        products_button = QPushButton("Manage Products")
        products_button.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        actions_layout.addWidget(products_button)
        
        layout.addLayout(actions_layout)
    
    def create_customers_tab(self):
        """Create the customers management tab."""
        customers_tab = QWidget()
        self.tab_widget.addTab(customers_tab, "Customers")
        
        # Implement customers UI (placeholder)
        layout = QVBoxLayout(customers_tab)
        label = QLabel("Customer management will be implemented here")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def create_products_tab(self):
        """Create the products management tab."""
        products_tab = QWidget()
        self.tab_widget.addTab(products_tab, "Products")
        
        # Implement products UI (placeholder)
        layout = QVBoxLayout(products_tab)
        label = QLabel("Product management will be implemented here")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def create_orders_tab(self):
        """Create the orders management tab."""
        orders_tab = OrdersTab(self.controller)
        self.tab_widget.addTab(orders_tab, "Orders")
    
    def create_reports_tab(self):
        """Create the reports tab."""
        reports_tab = QWidget()
        self.tab_widget.addTab(reports_tab, "Reports")
        
        # Implement reports UI (placeholder)
        layout = QVBoxLayout(reports_tab)
        label = QLabel("Reports will be implemented here")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def show_login_dialog(self):
        """Show the login dialog."""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            
            # Attempt login
            if self.controller.login(username, password):
                self.login_success()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
    
    def login_success(self):
        """Handle successful login."""
        # Update UI for logged-in state
        self.tab_widget.setEnabled(True)
        self.login_action.setEnabled(False)
        self.logout_action.setEnabled(True)
        
        # Update user info
        user = self.controller.current_user
        self.user_info_label.setText(f"Logged in as: {user.full_name or user.username}")
        
        # Show admin features if applicable
        is_admin = self.controller.is_admin()
        self.statusBar.showMessage(f"Logged in as: {user.username} ({'Admin' if is_admin else 'Cashier'})")
    
    def logout(self):
        """Log out the current user."""
        self.controller.logout()
        
        # Update UI for logged-out state
        self.tab_widget.setEnabled(False)
        self.login_action.setEnabled(True)
        self.logout_action.setEnabled(False)
        self.user_info_label.setText("Not logged in")
        self.statusBar.showMessage("Logged out")
    
    def create_new_order(self):
        """Create a new order."""
        # Check if user is logged in
        if not self.controller.current_user:
            QMessageBox.warning(self, "Not Logged In", "You must be logged in to create an order")
            return
        
        dialog = OrderDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the orders tab to show the new order
            orders_tab = self.tab_widget.widget(3)  # Orders tab is at index 3
            if isinstance(orders_tab, OrdersTab):
                orders_tab.refresh_orders()
                
            # Switch to the orders tab to show the new order
            self.tab_widget.setCurrentIndex(3)
    
    def backup_data(self):
        """Backup the application data."""
        # TODO: Implement file dialog for selecting backup location
        QMessageBox.information(self, "Backup", "Data backup will be implemented here")
    
    def restore_data(self):
        """Restore the application data from backup."""
        # TODO: Implement file dialog for selecting backup file
        QMessageBox.information(self, "Restore", "Data restore will be implemented here")
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Order Processing Application",
            "Order Processing Application\n\n"
            "A simple application for managing customer orders and payments.\n\n"
            "Version 1.0"
        )