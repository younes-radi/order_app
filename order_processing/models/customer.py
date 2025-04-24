"""
Customer model for the order processing application.
"""
import sqlite3
from typing import List, Optional
from ..utils.database import get_db_connection

class Customer:
    """
    Customer model representing business customers.
    """
    
    def __init__(
        self, customer_id: Optional[int] = None, name: str = "", 
        contact_number: str = "", email: str = "", address: str = ""
    ) -> None:
        """Initialize a customer instance."""
        self.customer_id = customer_id
        self.name = name
        self.contact_number = contact_number
        self.email = email
        self.address = address
    
    def save(self) -> bool:
        """Save the customer to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.customer_id:
                # Update existing customer
                cursor.execute(
                    "UPDATE customers SET name = ?, contact_number = ?, email = ?, address = ? WHERE customer_id = ?",
                    (self.name, self.contact_number, self.email, self.address, self.customer_id)
                )
            else:
                # Insert new customer
                cursor.execute(
                    "INSERT INTO customers (name, contact_number, email, address) VALUES (?, ?, ?, ?)",
                    (self.name, self.contact_number, self.email, self.address)
                )
                self.customer_id = cursor.lastrowid
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self) -> bool:
        """Delete the customer from the database."""
        if not self.customer_id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM customers WHERE customer_id = ?", (self.customer_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @classmethod
    def find_by_id(cls, customer_id: int) -> Optional['Customer']:
        """Find a customer by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                customer_id=row['customer_id'],
                name=row['name'],
                contact_number=row['contact_number'],
                email=row['email'],
                address=row['address']
            )
        return None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['Customer']:
        """Find a customer by email address."""
        if not email:
            return None
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                customer_id=row['customer_id'],
                name=row['name'],
                contact_number=row['contact_number'],
                email=row['email'],
                address=row['address']
            )
        return None
    
    @classmethod
    def find_all(cls) -> List['Customer']:
        """Find all customers."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            customer_id=row['customer_id'],
            name=row['name'],
            contact_number=row['contact_number'],
            email=row['email'],
            address=row['address']
        ) for row in rows]
    
    @classmethod
    def search(cls, query: str) -> List['Customer']:
        """Search for customers by name, email, or address."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ? OR address LIKE ? ORDER BY name",
            (search_term, search_term, search_term)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            customer_id=row['customer_id'],
            name=row['name'],
            contact_number=row['contact_number'],
            email=row['email'],
            address=row['address']
        ) for row in rows]