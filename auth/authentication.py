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
            user_data = self._get_user_by_username(username)
            
            if not user_data:
                return None
            
            if not self._verify_password(password, user_data['password_hash']):
                return None
            
            if user_data['user_type'] != user_type:
                return None
            
            if not user_data['is_active']:
                return None
            
            self._update_last_login(user_data['id'])
            
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
        """
        try:
            if self._get_user_by_username(username):
                return False
            
            password_hash = self._hash_password(password)
            
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
    
    def get_users_by_type(self, user_type: str) -> list:
        """Get all users of a specific type"""
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
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username"""
        query = 'SELECT * FROM users WHERE username = ? AND is_active = 1'
        return self.db_manager.fetch_one(query, (username,))
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?'
        self.db_manager.execute_query(query, (user_id,))
    
    def _ensure_default_users(self) -> None:
        """Create default users if none exist"""
        try:
            if self.db_manager.get_row_count('users') == 0:
                self.create_user('admin', 'admin123', 'Admin User', 'admin@calpoly.edu', 'auditor', 'Administration')
                self.create_user('demo_auditee', 'demo123', 'Demo Auditee', 'demo@calpoly.edu', 'auditee', 'Academic Affairs')
        except Exception as e:
            st.error(f"Error creating default users: {str(e)}")


class SessionValidator:
    """
    Validates user sessions and permissions
    """
    
    @staticmethod
    def is_session_valid(session_data: dict) -> bool:
        if not session_data:
            return False
        return all(field in session_data for field in ['id', 'username', 'user_type'])
    
    @staticmethod
    def has_permission(user_data: dict, permission: str) -> bool:
        if not user_data:
            return False
        
        permissions = {
            'auditor': ['create_audit', 'view_all_audits', 'review_documents', 'send_notifications'],
            'auditee': ['view_assigned_audits', 'upload_documents', 'view_notifications']
        }
        
        return permission in permissions.get(user_data.get('user_type'), [])