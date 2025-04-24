"""
Payment model for the order processing application.
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from ..utils.database import get_db_connection

class Payment:
    """
    Payment model representing order payments.
    """
    
    # Payment type constants
    TYPE_CASH = "cash"
    TYPE_CREDIT_CARD = "credit_card"
    TYPE_STORE_CREDIT = "store_credit"
    
    # Payment status constants
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"
    
    def __init__(
        self, payment_id: Optional[int] = None, order_id: Optional[int] = None,
        payment_date: Optional[datetime] = None, amount: float = 0.0,
        payment_type: str = TYPE_CASH, status: str = STATUS_PENDING,
        reference_number: str = ""
    ) -> None:
        """Initialize a payment instance."""
        self.payment_id = payment_id
        self.order_id = order_id
        self.payment_date = payment_date or datetime.now()
        self.amount = amount
        self.payment_type = payment_type
        self.status = status
        self.reference_number = reference_number
    
    def validate(self) -> List[str]:
        """Validate the payment data.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.order_id:
            errors.append("Order ID is required")
        
        if self.amount <= 0:
            errors.append("Payment amount must be positive")
        
        if self.payment_type not in [self.TYPE_CASH, self.TYPE_CREDIT_CARD, self.TYPE_STORE_CREDIT]:
            errors.append("Invalid payment type")
        
        if self.payment_type == self.TYPE_CREDIT_CARD and not self.reference_number:
            errors.append("Reference number is required for credit card payments")
        
        return errors
    
    def save(self) -> bool:
        """Save the payment to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.payment_id:
                # Update existing payment
                cursor.execute(
                    "UPDATE payments SET order_id = ?, payment_date = ?, amount = ?, payment_type = ?, status = ?, reference_number = ? WHERE payment_id = ?",
                    (self.order_id, self.payment_date, self.amount, self.payment_type, self.status, self.reference_number, self.payment_id)
                )
            else:
                # Insert new payment
                cursor.execute(
                    "INSERT INTO payments (order_id, payment_date, amount, payment_type, status, reference_number) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.order_id, self.payment_date, self.amount, self.payment_type, self.status, self.reference_number)
                )
                self.payment_id = cursor.lastrowid
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def refund(self) -> bool:
        """Mark the payment as refunded.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.payment_id or self.status == self.STATUS_REFUNDED:
            return False
        
        self.status = self.STATUS_REFUNDED
        return self.save()
    
    @classmethod
    def find_by_id(cls, payment_id: int) -> Optional['Payment']:
        """Find a payment by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                payment_id=row['payment_id'],
                order_id=row['order_id'],
                payment_date=row['payment_date'],
                amount=row['amount'],
                payment_type=row['payment_type'],
                status=row['status'],
                reference_number=row['reference_number']
            )
        return None
    
    @classmethod
    def find_by_order_id(cls, order_id: int) -> List['Payment']:
        """Find all payments for an order."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY payment_date DESC", (order_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            payment_id=row['payment_id'],
            order_id=row['order_id'],
            payment_date=row['payment_date'],
            amount=row['amount'],
            payment_type=row['payment_type'],
            status=row['status'],
            reference_number=row['reference_number']
        ) for row in rows]