"""
Order and OrderItem models for the order processing application.
"""
from typing import Any, Dict, List, Optional, Tuple
import sqlite3
from datetime import datetime
from . import BaseModel
from ..utils.database import get_db_connection

class OrderItem(BaseModel):
    """OrderItem model representing items in an order."""
    
    table_name = "order_items"
    primary_key = "order_item_id"
    
    def __init__(
        self,
        order_item_id: Optional[int] = None,
        order_id: Optional[int] = None,
        product_id: Optional[int] = None,
        quantity: int = 1,
        unit_price: float = 0.0
    ) -> None:
        """Initialize a new OrderItem instance.
        
        Args:
            order_item_id: The unique identifier for the order item
            order_id: The ID of the order this item belongs to
            product_id: The ID of the product in the order
            quantity: The quantity of the product
            unit_price: The unit price of the product at the time of order
        """
        super().__init__()
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self._product_name = None  # For caching product name
    
    @property
    def order_item_id(self) -> Optional[int]:
        """Get the order item ID."""
        return self._data.get("order_item_id")
    
    @order_item_id.setter
    def order_item_id(self, value: Optional[int]) -> None:
        """Set the order item ID.""" 
        self._data["order_item_id"] = value
    
    @property
    def order_id(self) -> Optional[int]:
        """Get the order ID."""
        return self._data.get("order_id")
    
    @order_id.setter
    def order_id(self, value: Optional[int]) -> None:
        """Set the order ID.""" 
        self._data["order_id"] = value
    
    @property
    def product_id(self) -> Optional[int]:
        """Get the product ID."""
        return self._data.get("product_id")
    
    @product_id.setter
    def product_id(self, value: Optional[int]) -> None:
        """Set the product ID.""" 
        self._data["product_id"] = value
    
    @property
    def quantity(self) -> int:
        """Get the quantity."""
        return self._data.get("quantity", 0)
    
    @quantity.setter
    def quantity(self, value: int) -> None:
        """Set the quantity.""" 
        self._data["quantity"] = value
    
    @property
    def unit_price(self) -> float:
        """Get the unit price."""
        return self._data.get("unit_price", 0.0)
    
    @unit_price.setter
    def unit_price(self, value: float) -> None:
        """Set the unit price.""" 
        self._data["unit_price"] = value
    
    @property
    def subtotal(self) -> float:
        """Calculate the subtotal for this item.
        
        Returns:
            The subtotal (quantity * unit_price)
        """
        return self.quantity * self.unit_price
    
    @property
    def total_price(self) -> float:
        """Calculate the total price for this item."""
        return self.quantity * self.unit_price
    
    @property
    def product_name(self) -> str:
        """Get the product name for this item."""
        if self._product_name is None and self.product_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products WHERE product_id = ?", (self.product_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                self._product_name = row['name']
            else:
                self._product_name = "Unknown Product"
        
        return self._product_name or "Unknown Product"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order item to dictionary.
        
        Returns:
            Dictionary representation of the order item
        """
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderItem':
        """Create an OrderItem instance from a dictionary.
        
        Args:
            data: Dictionary containing order item data
            
        Returns:
            A new OrderItem instance
        """
        order_item = cls()
        order_item._data = data.copy()
        return order_item
    
    @classmethod
    def create_tables(cls) -> None:
        """Create the order_items table if it doesn't exist."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )''')
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, order_item_id: int) -> Optional['OrderItem']:
        """Find an order item by its ID.
        
        Args:
            order_item_id: The ID of the order item to find
            
        Returns:
            OrderItem instance if found, None otherwise
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM order_items WHERE order_item_id = ?", (order_item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls.from_dict(dict(zip([col[0] for col in cursor.description], row)))
        return None
    
    @classmethod
    def find_by_order_id(cls, order_id: int) -> List['OrderItem']:
        """Find order items by order ID.
        
        Args:
            order_id: The ID of the order
            
        Returns:
            List of OrderItem instances
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls.from_dict(dict(zip([col[0] for col in cursor.description], row))) for row in rows]
    
    def save(self) -> 'OrderItem':
        """Save the order item to the database.
        
        Returns:
            The updated OrderItem instance
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.order_item_id is None:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (self.order_id, self.product_id, self.quantity, self.unit_price)
            )
            self.order_item_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE order_items SET order_id = ?, product_id = ?, quantity = ?, unit_price = ? WHERE order_item_id = ?",
                (self.order_id, self.product_id, self.quantity, self.unit_price, self.order_item_id)
            )
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self) -> bool:
        """Delete the order item.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if self.order_item_id is None:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items WHERE order_item_id = ?", (self.order_item_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            self.order_item_id = None
        
        return success


class Order(BaseModel):
    """Order model representing customer purchases."""
    
    table_name = "orders"
    primary_key = "order_id"
    
    # Order status constants
    STATUS_DRAFT = "draft"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    def __init__(
        self,
        order_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        order_date: Optional[datetime] = None,
        status: str = STATUS_DRAFT,
        total_cost: float = 0.0
    ) -> None:
        """Initialize a new Order instance.
        
        Args:
            order_id: The unique identifier for the order
            customer_id: The ID of the customer who placed the order
            order_date: The date and time when the order was created
            status: The current status of the order
            total_cost: The total cost of the order
        """
        super().__init__()
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date or datetime.now()
        self.status = status
        self.total_cost = total_cost
        self._customer_name = None  # For caching customer name
    
    @property
    def order_id(self) -> Optional[int]:
        """Get the order ID."""
        return self._data.get("order_id")
    
    @order_id.setter
    def order_id(self, value: Optional[int]) -> None:
        """Set the order ID.""" 
        self._data["order_id"] = value
    
    @property
    def customer_id(self) -> Optional[int]:
        """Get the customer ID.""" 
        return self._data.get("customer_id")
    
    @customer_id.setter
    def customer_id(self, value: Optional[int]) -> None:
        """Set the customer ID.""" 
        self._data["customer_id"] = value
    
    @property
    def order_date(self) -> datetime:
        """Get the order date.""" 
        return self._data.get("order_date", datetime.now())
    
    @order_date.setter
    def order_date(self, value: datetime) -> None:
        """Set the order date.""" 
        self._data["order_date"] = value
    
    @property
    def status(self) -> str:
        """Get the order status.""" 
        return self._data.get("status", self.STATUS_DRAFT)
    
    @status.setter
    def status(self, value: str) -> None:
        """Set the order status.""" 
        self._data["status"] = value
    
    @property
    def total_cost(self) -> float:
        """Get the total cost.""" 
        return self._data.get("total_cost", 0.0)
    
    @total_cost.setter
    def total_cost(self, value: float) -> None:
        """Set the total cost.""" 
        self._data["total_cost"] = value
    
    @property
    def customer_name(self) -> str:
        """Get the customer name for this order."""
        if self._customer_name is None and self.customer_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM customers WHERE customer_id = ?", (self.customer_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                self._customer_name = row['name']
            else:
                self._customer_name = "Unknown Customer"
        
        return self._customer_name or "Unknown Customer"
    
    def add_item(self, product_id: int, quantity: int, unit_price: float) -> 'OrderItem':
        """Add an item to the order.
        
        Args:
            product_id: The ID of the product
            quantity: The quantity of the product
            unit_price: The unit price of the product
            
        Returns:
            The newly created OrderItem
        """
        if self.order_id is None:
            self.save()
        
        order_item = OrderItem(
            order_id=self.order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        order_item.save()
        
        # Update total cost
        self.recalculate_total()
        self.save()
        
        return order_item
    
    def get_items(self) -> List['OrderItem']:
        """Get all items in the order.
        
        Returns:
            List of OrderItem instances
        """
        if self.order_id is None:
            return []
        
        return OrderItem.find_by_order_id(self.order_id)
    
    def remove_item(self, order_item_id: int) -> bool:
        """Remove an item from the order.
        
        Args:
            order_item_id: The ID of the order item to remove
            
        Returns:
            True if the item was removed, False otherwise
        """
        order_item = OrderItem.find_by_id(order_item_id)
        if order_item is None or order_item.order_id != self.order_id:
            return False
        
        if order_item.delete():
            self.recalculate_total()
            self.save()
            return True
        
        return False
    
    def recalculate_total(self) -> None:
        """Recalculate the total cost of the order."""
        items = self.get_items()
        total = sum(item.quantity * item.unit_price for item in items)
        self.total_cost = total
    
    def cancel(self) -> bool:
        """Cancel the order.
        
        Returns:
            True if the order was cancelled, False otherwise
        """
        if self.status in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            return False
        
        self.status = self.STATUS_CANCELLED
        self.save()
        return True
    
    def complete(self) -> bool:
        """Mark the order as completed.
        
        Returns:
            True if the order was completed, False otherwise
        """
        if self.status != self.STATUS_PROCESSING:
            return False
        
        self.status = self.STATUS_COMPLETED
        self.save()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary.
        
        Returns:
            Dictionary representation of the order
        """
        data = self._data.copy()
        if isinstance(data.get("order_date"), datetime):
            data["order_date"] = data["order_date"].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create an Order instance from a dictionary.
        
        Args:
            data: Dictionary containing order data
            
        Returns:
            A new Order instance
        """
        order = cls()
        order_data = data.copy()
        
        # Convert string date to datetime if needed
        if isinstance(order_data.get("order_date"), str):
            try:
                order_data["order_date"] = datetime.fromisoformat(order_data["order_date"])
            except (ValueError, TypeError):
                order_data["order_date"] = datetime.now()
        
        order._data = order_data
        return order
    
    @classmethod
    def create_tables(cls) -> None:
        """Create the orders table if it doesn't exist."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            total_cost REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )''')
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, order_id: int) -> Optional['Order']:
        """Find an order by its ID.
        
        Args:
            order_id: The ID of the order to find
            
        Returns:
            Order instance if found, None otherwise
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls.from_dict(dict(zip([col[0] for col in cursor.description], row)))
        return None
    
    @classmethod
    def find_by_customer_id(cls, customer_id: int) -> List['Order']:
        """Find orders by customer ID.
        
        Args:
            customer_id: The ID of the customer
            
        Returns:
            List of Order instances
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC", (customer_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls.from_dict(dict(zip([col[0] for col in cursor.description], row))) for row in rows]
    
    @classmethod
    def find_by_date_range(cls, start_date: datetime, end_date: datetime) -> List['Order']:
        """Find orders within a date range.
        
        Args:
            start_date: The start date of the range
            end_date: The end date of the range
            
        Returns:
            List of Order instances
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE order_date BETWEEN ? AND ? ORDER BY order_date DESC",
            (start_date.isoformat(), end_date.isoformat())
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls.from_dict(dict(zip([col[0] for col in cursor.description], row))) for row in rows]
    
    @classmethod
    def find_all(cls) -> List['Order']:
        """Get all orders.
        
        Returns:
            List of all Order instances
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls.from_dict(dict(zip([col[0] for col in cursor.description], row))) for row in rows]
    
    @classmethod
    def find_by_status(cls, status: str) -> List['Order']:
        """Find orders by status.
        
        Args:
            status: The status to search for
            
        Returns:
            List of matching Order instances
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY order_date DESC", (status,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls.from_dict(dict(zip([col[0] for col in cursor.description], row))) for row in rows]
    
    def save(self) -> 'Order':
        """Save the order to the database.
        
        Returns:
            The updated Order instance
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure order_date is in ISO format for storage
        order_date_str = self.order_date.isoformat()
        
        if self.order_id is None:
            cursor.execute(
                "INSERT INTO orders (customer_id, order_date, status, total_cost) VALUES (?, ?, ?, ?)",
                (self.customer_id, order_date_str, self.status, self.total_cost)
            )
            self.order_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE orders SET customer_id = ?, order_date = ?, status = ?, total_cost = ? WHERE order_id = ?",
                (self.customer_id, order_date_str, self.status, self.total_cost, self.order_id)
            )
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self) -> bool:
        """Delete the order and all its items.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if self.order_id is None:
            return False
        
        # Delete related order items first
        items = self.get_items()
        for item in items:
            item.delete()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (self.order_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            self.order_id = None
        
        return success