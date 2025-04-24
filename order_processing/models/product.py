"""
Product model for the order processing application.
"""
import sqlite3
from typing import List, Optional
from ..utils.database import get_db_connection

class Product:
    """
    Product model representing inventory items.
    """
    
    def __init__(
        self, product_id: Optional[int] = None, name: str = "", sku: str = "",
        description: str = "", price: float = 0.0, stock_quantity: int = 0
    ) -> None:
        """Initialize a product instance."""
        self.product_id = product_id
        self.name = name
        self.sku = sku
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
    
    def save(self) -> bool:
        """Save the product to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.product_id:
                # Update existing product
                cursor.execute(
                    "UPDATE products SET name = ?, sku = ?, description = ?, price = ?, stock_quantity = ? WHERE product_id = ?",
                    (self.name, self.sku, self.description, self.price, self.stock_quantity, self.product_id)
                )
            else:
                # Insert new product
                cursor.execute(
                    "INSERT INTO products (name, sku, description, price, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                    (self.name, self.sku, self.description, self.price, self.stock_quantity)
                )
                self.product_id = cursor.lastrowid
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self) -> bool:
        """Delete the product from the database."""
        if not self.product_id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM products WHERE product_id = ?", (self.product_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_stock(self, quantity_change: int) -> bool:
        """Update the product's stock quantity.
        
        Args:
            quantity_change: The amount to change the stock (positive or negative)
            
        Returns:
            True if the update succeeded, False otherwise
        """
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            return False
        
        self.stock_quantity = new_quantity
        return True
    
    @classmethod
    def find_by_id(cls, product_id: int) -> Optional['Product']:
        """Find a product by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                product_id=row['product_id'],
                name=row['name'],
                sku=row['sku'],
                description=row['description'],
                price=row['price'],
                stock_quantity=row['stock_quantity']
            )
        return None
    
    @classmethod
    def find_by_sku(cls, sku: str) -> Optional['Product']:
        """Find a product by SKU."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                product_id=row['product_id'],
                name=row['name'],
                sku=row['sku'],
                description=row['description'],
                price=row['price'],
                stock_quantity=row['stock_quantity']
            )
        return None
    
    @classmethod
    def find_all(cls) -> List['Product']:
        """Find all products."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            product_id=row['product_id'],
            name=row['name'],
            sku=row['sku'],
            description=row['description'],
            price=row['price'],
            stock_quantity=row['stock_quantity']
        ) for row in rows]
    
    @classmethod
    def search(cls, query: str) -> List['Product']:
        """Search for products by name, SKU, or description."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR sku LIKE ? OR description LIKE ? ORDER BY name",
            (search_term, search_term, search_term)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            product_id=row['product_id'],
            name=row['name'],
            sku=row['sku'],
            description=row['description'],
            price=row['price'],
            stock_quantity=row['stock_quantity']
        ) for row in rows]
    
    @classmethod
    def find_low_stock(cls, threshold: int = 10) -> List['Product']:
        """Find products with stock below the given threshold."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE stock_quantity < ? ORDER BY stock_quantity", (threshold,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            product_id=row['product_id'],
            name=row['name'],
            sku=row['sku'],
            description=row['description'],
            price=row['price'],
            stock_quantity=row['stock_quantity']
        ) for row in rows]