"""
Model classes for the order processing application.
"""
"""
Base model for all database models in the order processing application.
"""
from typing import Dict, Any, ClassVar, Optional
import sqlite3
import os

class BaseModel:
    """Base class for all database models.
    
    This class provides common functionality for all database models,
    including database connection, CRUD operations, and data handling.
    """
    
    table_name: ClassVar[str] = ""
    primary_key: ClassVar[str] = ""
    
    def __init__(self) -> None:
        """Initialize a new BaseModel instance."""
        self._data: Dict[str, Any] = {}
    
    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Get a connection to the SQLite database.
        
        Returns:
            An open SQLite database connection
        """
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Open connection to database
        conn = sqlite3.connect("data/order_processing.db")
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Configure connection
        conn.row_factory = sqlite3.Row
        
        return conn