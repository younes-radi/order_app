"""
User model for the order processing application.
"""
import bcrypt
import sqlite3
from typing import List, Optional
from ..utils.database import get_db_connection

class Role:
    """
    Role model representing user roles in the system.
    """
    
    def __init__(
        self, role_id: Optional[int] = None, name: str = "", description: str = ""
    ) -> None:
        """Initialize a role instance."""
        self.role_id = role_id
        self.name = name
        self.description = description
    
    def save(self) -> bool:
        """Save the role to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.role_id:
                # Update existing role
                cursor.execute(
                    "UPDATE roles SET name = ?, description = ? WHERE role_id = ?",
                    (self.name, self.description, self.role_id)
                )
            else:
                # Insert new role
                cursor.execute(
                    "INSERT INTO roles (name, description) VALUES (?, ?)",
                    (self.name, self.description)
                )
                self.role_id = cursor.lastrowid
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self) -> bool:
        """Delete the role from the database."""
        if not self.role_id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if role is being used by any users
            cursor.execute("SELECT COUNT(*) FROM users WHERE role_id = ?", (self.role_id,))
            if cursor.fetchone()[0] > 0:
                return False
            
            cursor.execute("DELETE FROM roles WHERE role_id = ?", (self.role_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @classmethod
    def find_by_id(cls, role_id: int) -> Optional['Role']:
        """Find a role by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM roles WHERE role_id = ?", (role_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(role_id=row['role_id'], name=row['name'], description=row['description'])
        return None
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Role']:
        """Find a role by name."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM roles WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(role_id=row['role_id'], name=row['name'], description=row['description'])
        return None
    
    @classmethod
    def find_all(cls) -> List['Role']:
        """Find all roles."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM roles ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(role_id=row['role_id'], name=row['name'], description=row['description']) for row in rows]

class User:
    """
    User model representing system users.
    """
    
    def __init__(
        self, user_id: Optional[int] = None, username: str = "", password_hash: str = "",
        full_name: str = "", email: str = "", role_id: Optional[int] = None
    ) -> None:
        """Initialize a user instance."""
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.role_id = role_id
    
    def set_password(self, password: str) -> None:
        """Set the user's password (hashed)."""
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
    
    def save(self) -> bool:
        """Save the user to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.user_id:
                # Update existing user
                cursor.execute(
                    "UPDATE users SET username = ?, password_hash = ?, full_name = ?, email = ?, role_id = ? WHERE user_id = ?",
                    (self.username, self.password_hash, self.full_name, self.email, self.role_id, self.user_id)
                )
            else:
                # Insert new user
                cursor.execute(
                    "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (?, ?, ?, ?, ?)",
                    (self.username, self.password_hash, self.full_name, self.email, self.role_id)
                )
                self.user_id = cursor.lastrowid
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self) -> bool:
        """Delete the user from the database."""
        if not self.user_id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM users WHERE user_id = ?", (self.user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """Find a user by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                user_id=row['user_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                full_name=row['full_name'],
                email=row['email'],
                role_id=row['role_id']
            )
        return None
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Find a user by username."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(
                user_id=row['user_id'],
                username=row['username'],
                password_hash=row['password_hash'],
                full_name=row['full_name'],
                email=row['email'],
                role_id=row['role_id']
            )
        return None
    
    @classmethod
    def find_all(cls) -> List['User']:
        """Find all users."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY username")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(
            user_id=row['user_id'],
            username=row['username'],
            password_hash=row['password_hash'],
            full_name=row['full_name'],
            email=row['email'],
            role_id=row['role_id']
        ) for row in rows]