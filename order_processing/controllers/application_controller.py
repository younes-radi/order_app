"""
Main controller for the order processing application.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os
from order_processing.models.user import User, Role
from order_processing.models.customer import Customer
from order_processing.models.product import Product
from order_processing.models.order import Order, OrderItem
from order_processing.models.payment import Payment
from order_processing.utils.database import init_database, seed_default_data, backup_database, restore_database

class ApplicationController:
    """Controller class for the order processing application.
    
    This class serves as the main controller for the application,
    handling the core business logic and interactions between
    the views and the models.
    """
    
    def __init__(self) -> None:
        """Initialize the application controller."""
        self._current_user: Optional[User] = None
        self._current_order: Optional[Order] = None
        
        # Initialize the database
        init_database()
        seed_default_data()
    
    @property
    def current_user(self) -> Optional[User]:
        """Get the currently logged-in user."""
        return self._current_user
    
    @property
    def current_order(self) -> Optional[Order]:
        """Get the current active order."""
        return self._current_order
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate a user.
        
        Args:
            username: Username for login
            password: Password for login
            
        Returns:
            True if authentication succeeded, False otherwise
        """
        user = User.find_by_username(username)
        if user and user.check_password(password):
            self._current_user = user
            return True
        return False
    
    def logout(self) -> None:
        """Log out the current user."""
        self._current_user = None
    
    def is_admin(self) -> bool:
        """Check if the current user has admin privileges.
        
        Returns:
            True if the user is an admin, False otherwise
        """
        if not self._current_user or not self._current_user.role_id:
            return False
        
        role = Role.find_by_id(self._current_user.role_id)
        return role and role.name == "Admin"
    
    # Customer Management
    
    def add_customer(
        self, name: str, contact_number: str, email: str, address: str
    ) -> Tuple[bool, Optional[Customer], str]:
        """Add a new customer.
        
        Args:
            name: Customer name
            contact_number: Customer contact number
            email: Customer email address
            address: Customer physical address
            
        Returns:
            Tuple of (success, customer, error_message)
        """
        # Basic validation
        if not name:
            return False, None, "Name is required"
        
        # Check if customer with email already exists
        if email and Customer.find_by_email(email):
            return False, None, "A customer with this email already exists"
        
        try:
            customer = Customer(
                name=name,
                contact_number=contact_number,
                email=email,
                address=address
            )
            customer.save()
            return True, customer, ""
        except Exception as e:
            return False, None, f"Error adding customer: {str(e)}"
    
    def update_customer(
        self, customer_id: int, name: str, contact_number: str, email: str, address: str
    ) -> Tuple[bool, Optional[Customer], str]:
        """Update an existing customer.
        
        Args:
            customer_id: ID of the customer to update
            name: Updated customer name
            contact_number: Updated contact number
            email: Updated email address
            address: Updated physical address
            
        Returns:
            Tuple of (success, customer, error_message)
        """
        # Basic validation
        if not name:
            return False, None, "Name is required"
        
        # Check if customer exists
        customer = Customer.find_by_id(customer_id)
        if not customer:
            return False, None, "Customer not found"
        
        # Check if email is already used by another customer
        if email:
            existing = Customer.find_by_email(email)
            if existing and existing.customer_id != customer_id:
                return False, None, "Email is already used by another customer"
        
        try:
            customer.name = name
            customer.contact_number = contact_number
            customer.email = email
            customer.address = address
            customer.save()
            return True, customer, ""
        except Exception as e:
            return False, None, f"Error updating customer: {str(e)}"
    
    def delete_customer(self, customer_id: int) -> Tuple[bool, str]:
        """Delete a customer.
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if customer exists
        customer = Customer.find_by_id(customer_id)
        if not customer:
            return False, "Customer not found"
        
        # Check if customer has orders
        orders = Order.find_by_customer_id(customer_id)
        if orders:
            return False, "Cannot delete customer with existing orders"
        
        try:
            if customer.delete():
                return True, ""
            return False, "Failed to delete customer"
        except Exception as e:
            return False, f"Error deleting customer: {str(e)}"
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers.
        
        Returns:
            List of all Customer instances
        """
        return Customer.find_all()
    
    def search_customers(self, query: str) -> List[Customer]:
        """Search for customers.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Customer instances
        """
        return Customer.search(query)
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Customer instance if found, None otherwise
        """
        return Customer.find_by_id(customer_id)
    
    # Product Management
    
    def add_product(
        self, name: str, sku: str, description: str, price: float, stock_quantity: int
    ) -> Tuple[bool, Optional[Product], str]:
        """Add a new product.
        
        Args:
            name: Product name
            sku: Stock keeping unit (unique product code)
            description: Product description
            price: Product price
            stock_quantity: Initial stock quantity
            
        Returns:
            Tuple of (success, product, error_message)
        """
        # Basic validation
        if not name:
            return False, None, "Name is required"
        if not sku:
            return False, None, "SKU is required"
        if price < 0:
            return False, None, "Price cannot be negative"
        if stock_quantity < 0:
            return False, None, "Stock quantity cannot be negative"
        
        # Check if product with SKU already exists
        if Product.find_by_sku(sku):
            return False, None, "A product with this SKU already exists"
        
        try:
            product = Product(
                name=name,
                sku=sku,
                description=description,
                price=price,
                stock_quantity=stock_quantity
            )
            product.save()
            return True, product, ""
        except Exception as e:
            return False, None, f"Error adding product: {str(e)}"
    
    def update_product(
        self, product_id: int, name: str, sku: str, description: str, price: float, stock_quantity: int
    ) -> Tuple[bool, Optional[Product], str]:
        """Update an existing product.
        
        Args:
            product_id: ID of the product to update
            name: Updated product name
            sku: Updated SKU
            description: Updated description
            price: Updated price
            stock_quantity: Updated stock quantity
            
        Returns:
            Tuple of (success, product, error_message)
        """
        # Basic validation
        if not name:
            return False, None, "Name is required"
        if not sku:
            return False, None, "SKU is required"
        if price < 0:
            return False, None, "Price cannot be negative"
        if stock_quantity < 0:
            return False, None, "Stock quantity cannot be negative"
        
        # Check if product exists
        product = Product.find_by_id(product_id)
        if not product:
            return False, None, "Product not found"
        
        # Check if SKU is already used by another product
        if sku != product.sku:
            existing = Product.find_by_sku(sku)
            if existing and existing.product_id != product_id:
                return False, None, "SKU is already used by another product"
        
        try:
            product.name = name
            product.sku = sku
            product.description = description
            product.price = price
            product.stock_quantity = stock_quantity
            product.save()
            return True, product, ""
        except Exception as e:
            return False, None, f"Error updating product: {str(e)}"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """Delete a product.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if product exists
        product = Product.find_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        # TODO: Check if product is used in any order
        # This would require a more complex query than we have now
        
        try:
            if product.delete():
                return True, ""
            return False, "Failed to delete product"
        except Exception as e:
            return False, f"Error deleting product: {str(e)}"
    
    def get_all_products(self) -> List[Product]:
        """Get all products.
        
        Returns:
            List of all Product instances
        """
        return Product.find_all()
    
    def search_products(self, query: str) -> List[Product]:
        """Search for products.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Product instances
        """
        return Product.search(query)
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """Get products with low stock.
        
        Args:
            threshold: Stock quantity threshold
            
        Returns:
            List of Product instances with stock below threshold
        """
        return Product.find_low_stock(threshold)
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID.
        
        Args:
            product_id: ID of the product to retrieve
            
        Returns:
            Product instance if found, None otherwise
        """
        return Product.find_by_id(product_id)
    
    # Order Management
    
    def create_order(self, customer_id: int) -> Tuple[bool, Optional[Order], str]:
        """Create a new order.
        
        Args:
            customer_id: ID of the customer placing the order
            
        Returns:
            Tuple of (success, order, error_message)
        """
        # Check if customer exists
        customer = Customer.find_by_id(customer_id)
        if not customer:
            return False, None, "Customer not found"
        
        try:
            order = Order(
                customer_id=customer_id,
                order_date=datetime.now(),
                status=Order.STATUS_DRAFT,
                total_cost=0.0
            )
            order.save()
            self._current_order = order
            return True, order, ""
        except Exception as e:
            return False, None, f"Error creating order: {str(e)}"
    
    def add_order_item(
        self, product_id: int, quantity: int
    ) -> Tuple[bool, Optional[OrderItem], str]:
        """Add an item to the current order.
        
        Args:
            product_id: ID of the product to add
            quantity: Quantity of the product
            
        Returns:
            Tuple of (success, order_item, error_message)
        """
        if not self._current_order:
            return False, None, "No active order"
        
        if quantity <= 0:
            return False, None, "Quantity must be positive"
        
        # Check if product exists and has sufficient stock
        product = Product.find_by_id(product_id)
        if not product:
            return False, None, "Product not found"
        
        if product.stock_quantity < quantity:
            return False, None, "Insufficient stock"
        
        try:
            # Add item to order
            order_item = self._current_order.add_item(
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price
            )
            
            # Update product stock
            product.update_stock(-quantity)
            product.save()
            
            return True, order_item, ""
        except Exception as e:
            return False, None, f"Error adding order item: {str(e)}"
    
    def remove_order_item(self, order_item_id: int) -> Tuple[bool, str]:
        """Remove an item from the current order.
        
        Args:
            order_item_id: ID of the order item to remove
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self._current_order:
            return False, "No active order"
        
        # Get the order item
        order_item = OrderItem.find_by_id(order_item_id)
        if not order_item or order_item.order_id != self._current_order.order_id:
            return False, "Order item not found"
        
        # Get the product to update stock
        product = Product.find_by_id(order_item.product_id)
        if product:
            # Return the items to stock
            product.update_stock(order_item.quantity)
            product.save()
        
        # Remove the item
        if self._current_order.remove_item(order_item_id):
            return True, ""
        return False, "Failed to remove order item"
    
    def update_order_item_quantity(
        self, order_item_id: int, new_quantity: int
    ) -> Tuple[bool, str]:
        """Update the quantity of an item in the current order.
        
        Args:
            order_item_id: ID of the order item to update
            new_quantity: New quantity of the product
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self._current_order:
            return False, "No active order"
        
        if new_quantity <= 0:
            return False, "Quantity must be positive"
        
        # Get the order item
        order_item = OrderItem.find_by_id(order_item_id)
        if not order_item or order_item.order_id != self._current_order.order_id:
            return False, "Order item not found"
        
        # Get the product to check stock
        product = Product.find_by_id(order_item.product_id)
        if not product:
            return False, "Product not found"
        
        # Calculate the stock change
        quantity_change = new_quantity - order_item.quantity
        
        # Check if there's enough stock for the increase
        if quantity_change > 0 and product.stock_quantity < quantity_change:
            return False, "Insufficient stock"
        
        try:
            # Update product stock
            product.update_stock(-quantity_change)
            product.save()
            
            # Update order item
            order_item.quantity = new_quantity
            order_item.save()
            
            # Recalculate order total
            self._current_order.recalculate_total()
            self._current_order.save()
            
            return True, ""
        except Exception as e:
            return False, f"Error updating order item: {str(e)}"
    
    def get_order_items(self) -> List[OrderItem]:
        """Get items in the current order.
        
        Returns:
            List of OrderItem instances in the current order
        """
        if not self._current_order:
            return []
        
        return self._current_order.get_items()
    
    def cancel_order(self) -> Tuple[bool, str]:
        """Cancel the current order.
        
        Returns:
            Tuple of (success, error_message)
        """
        if not self._current_order:
            return False, "No active order"
        
        # Return all items to stock
        for item in self._current_order.get_items():
            product = Product.find_by_id(item.product_id)
            if product:
                product.update_stock(item.quantity)
                product.save()
        
        # Cancel the order
        if self._current_order.cancel():
            self._current_order = None
            return True, ""
        return False, "Failed to cancel order"
    
    def process_payment(
        self, amount: float, payment_type: str, reference_number: str = ""
    ) -> Tuple[bool, Optional[Payment], str]:
        """Process a payment for the current order.
        
        Args:
            amount: Payment amount
            payment_type: Type of payment (cash, credit_card, store_credit)
            reference_number: Reference number for the payment
            
        Returns:
            Tuple of (success, payment, error_message)
        """
        if not self._current_order:
            return False, None, "No active order"
        
        # Validate payment
        if amount <= 0:
            return False, None, "Payment amount must be positive"
        
        if amount < self._current_order.total_cost:
            return False, None, "Payment amount is less than the order total"
        
        if payment_type not in [Payment.TYPE_CASH, Payment.TYPE_CREDIT_CARD, Payment.TYPE_STORE_CREDIT]:
            return False, None, "Invalid payment type"
        
        if payment_type == Payment.TYPE_CREDIT_CARD and not reference_number:
            return False, None, "Reference number is required for credit card payments"
        
        try:
            # Create and save the payment
            payment = Payment(
                order_id=self._current_order.order_id,
                payment_date=datetime.now(),
                amount=amount,
                payment_type=payment_type,
                status=Payment.STATUS_COMPLETED,
                reference_number=reference_number
            )
            
            # Validate the payment
            validation_errors = payment.validate()
            if validation_errors:
                return False, None, "\n".join(validation_errors)
            
            payment.save()
            
            # Update order status
            self._current_order.status = Order.STATUS_COMPLETED
            self._current_order.save()
            
            # Reset current order
            completed_order = self._current_order
            self._current_order = None
            
            return True, payment, ""
        except Exception as e:
            return False, None, f"Error processing payment: {str(e)}"
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get an order by ID.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            Order instance if found, None otherwise
        """
        return Order.find_by_id(order_id)
    
    def get_customer_orders(self, customer_id: int) -> List[Order]:
        """Get orders for a customer.
        
        Args:
            customer_id: The ID of the customer
            
        Returns:
            List of Order instances for the customer
        """
        return Order.find_by_customer_id(customer_id)
    
    def get_orders_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Get orders within a date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            List of Order instances in the date range
        """
        return Order.find_by_date_range(start_date, end_date)
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status.
        
        Args:
            status: Order status to filter by
            
        Returns:
            List of Order instances with the specified status
        """
        return Order.find_by_status(status)
    
    # Backup and Restore
    
    def backup_data(self, backup_path: str) -> Tuple[bool, str]:
        """Create a backup of the application data.
        
        Args:
            backup_path: Path where the backup should be saved
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if backup_database(backup_path):
                return True, ""
            return False, "Backup failed"
        except Exception as e:
            return False, f"Error creating backup: {str(e)}"
    
    def restore_data(self, backup_path: str) -> Tuple[bool, str]:
        """Restore application data from a backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if restore_database(backup_path):
                return True, ""
            return False, "Restore failed"
        except Exception as e:
            return False, f"Error restoring data: {str(e)}"