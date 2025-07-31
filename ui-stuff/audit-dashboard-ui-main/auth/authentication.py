"""
Authentication Manager for Cal Poly SLO Audit Management System

This module handles user authentication, password hashing, and user management.
It provides secure login functionality and user session management.
"""

import bcrypt
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st

from config.settings import AppConfig, DatabaseConfig
from utils.database_manager import DatabaseManager

class AuthenticationManager:
    """
    Manages user authentication and authorization for the audit system
    """
    
    def __init__(self):
        """
        Initialize the authentication manager with database connection
        """
        self.db_manager = DatabaseManager()
        self._ensure_default_users()
    
    def authenticate_user(self, username: str, password: str, user_type: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username, password, and user type
        
        Args:
            username: User's username
            password: User's password (plain text)
            user_type: Type of user ('auditor' or 'auditee')
            
        Returns:
            User data dictionary if authentication successful, None otherwise
        """
        try:
            # Get user from database
            user_data = self._get_user_by_username(username)
            
            if not user_data:
                return None
            
            # Verify password
            if not self._verify_password(password, user_data['password_hash']):
                return None
            
            # Verify user type matches
            if user_data['user_type'] != user_type:
                return None
            
            # Check if user is active
            if not user_data['is_active']:
                return None
            
            # Update last login
            self._update_last_login(user_data['id'])
            
            # Return user data (excluding password hash)
            return {
                'id': user_data['id'],
                'username': user_data['username'],
                'name': user_data['name'],
                'email': user_data['email'],
                'user_type': user_data['user_type'],
                'department': user_data['department'],
                'last_login': datetime.now()
            }
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def create_user(self, username: str, password: str, name: str, email: str, 
                   user_type: str, department: str = None) -> bool:
        """
        Create a new user account
        
        Args:
            username: Unique username
            password: Plain text password
            name: Full name
            email: Email address
            user_type: 'auditor' or 'auditee'
            department: User's department (optional)
            
        Returns:
            True if user created successfully, False otherwise
        """
        try:
            # Check if username already exists
            if self._get_user_by_username(username):
                return False
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Insert user into database
            query = '''
                INSERT INTO users (username, password_hash, name, email, user_type, department)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            self.db_manager.execute_query(
                query, 
                (username, password_hash, name, email, user_type, department)
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return False
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user's password
        
        Args:
            user_id: User's ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            # Get current user data
            user_data = self._get_user_by_id(user_id)
            if not user_data:
                return False
            
            # Verify old password
            if not self._verify_password(old_password, user_data['password_hash']):
                return False
            
            # Validate new password
            if len(new_password) < AppConfig.PASSWORD_MIN_LENGTH:
                return False
            
            # Hash new password
            new_password_hash = self._hash_password(new_password)
            
            # Update password in database
            query = 'UPDATE users SET password_hash = ? WHERE id = ?'
            self.db_manager.execute_query(query, (new_password_hash, user_id))
            
            return True
            
        except Exception as e:
            st.error(f"Error changing password: {str(e)}")
            return False
    
    def get_users_by_type(self, user_type: str) -> list:
        """
        Get all users of a specific type
        
        Args:
            user_type: 'auditor' or 'auditee'
            
        Returns:
            List of user dictionaries
        """
        try:
            query = '''
                SELECT id, username, name, email, department, created_at, last_login, is_active
                FROM users 
                WHERE user_type = ? AND is_active = 1
                ORDER BY name
            '''
            
            return self.db_manager.fetch_all(query, (user_type,))
            
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []
    
    def get_users_by_department(self, department: str) -> list:
        """
        Get all users in a specific department
        
        Args:
            department: Department name
            
        Returns:
            List of user dictionaries
        """
        try:
            query = '''
                SELECT id, username, name, email, user_type, created_at, last_login, is_active
                FROM users 
                WHERE department = ? AND is_active = 1
                ORDER BY name
            '''
            
            return self.db_manager.fetch_all(query, (department,))
            
        except Exception as e:
            st.error(f"Error fetching users by department: {str(e)}")
            return []
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account
        
        Args:
            user_id: User's ID
            
        Returns:
            True if user deactivated successfully, False otherwise
        """
        try:
            query = 'UPDATE users SET is_active = 0 WHERE id = ?'
            self.db_manager.execute_query(query, (user_id,))
            return True
            
        except Exception as e:
            st.error(f"Error deactivating user: {str(e)}")
            return False
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by username
        
        Args:
            username: Username to search for
            
        Returns:
            User data dictionary or None if not found
        """
        query = 'SELECT * FROM users WHERE username = ? AND is_active = 1'
        return self.db_manager.fetch_one(query, (username,))
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User data dictionary or None if not found
        """
        query = 'SELECT * FROM users WHERE id = ? AND is_active = 1'
        return self.db_manager.fetch_one(query, (user_id,))
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _update_last_login(self, user_id: int) -> None:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User's ID
        """
        query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?'
        self.db_manager.execute_query(query, (user_id,))
    
    def _ensure_default_users(self) -> None:
        """
        Create default users if they don't exist (for development/testing)
        """
        try:
            # Check if any users exist
            existing_users = self.db_manager.fetch_all('SELECT COUNT(*) as count FROM users')
            
            if existing_users and existing_users[0]['count'] == 0:
                # Create default auditor
                self.create_user(
                    username='auditor1',
                    password='password123',
                    name='John Smith',
                    email='jsmith@calpoly.edu',
                    user_type='auditor',
                    department='Administration and Finance'
                )
                
                # Create default auditee
                self.create_user(
                    username='auditee1',
                    password='password123',
                    name='Jane Doe',
                    email='jdoe@calpoly.edu',
                    user_type='auditee',
                    department='Academic Affairs'
                )
                
                print("Default users created for development")
                
        except Exception as e:
            print(f"Error creating default users: {str(e)}")

class SessionValidator:
    """
    Validates and manages user sessions
    """
    
    @staticmethod
    def is_session_valid(session_data: Dict[str, Any]) -> bool:
        """
        Check if a user session is still valid
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            True if session is valid, False otherwise
        """
        if not session_data:
            return False
        
        # Check if session has required fields
        required_fields = ['id', 'username', 'user_type', 'last_login']
        if not all(field in session_data for field in required_fields):
            return False
        
        # Check session timeout
        last_login = session_data.get('last_login')
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
        
        if datetime.now() - last_login > timedelta(minutes=AppConfig.SESSION_TIMEOUT_MINUTES):
            return False
        
        return True
    
    @staticmethod
    def has_permission(user_data: Dict[str, Any], required_permission: str) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_data: User data dictionary
            required_permission: Required permission level
            
        Returns:
            True if user has permission, False otherwise
        """
        user_type = user_data.get('user_type', '').lower()
        
        # Define permission hierarchy
        permissions = {
            'auditor': ['create_audit', 'view_all_documents', 'manage_compliance', 'send_notifications'],
            'auditee': ['upload_documents', 'view_own_documents', 'respond_to_requests']
        }
        
        return required_permission in permissions.get(user_type, [])
