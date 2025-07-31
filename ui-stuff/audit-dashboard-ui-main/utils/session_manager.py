"""
Session Manager for Cal Poly SLO Audit Management System

This module handles user session management, including session storage,
validation, and cleanup for the Streamlit application.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

from config.settings import AppConfig
from auth.authentication import SessionValidator

class SessionManager:
    """
    Manages user sessions for the audit management system
    """
    
    def __init__(self):
        """
        Initialize session manager
        """
        self.session_key = 'audit_user_session'
        self.activity_key = 'last_activity'
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """
        Initialize session state if not already done
        """
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = None
        
        if self.activity_key not in st.session_state:
            st.session_state[self.activity_key] = datetime.now()
    
    def set_user_session(self, user_data: Dict[str, Any]) -> None:
        """
        Set user session data
        
        Args:
            user_data: Dictionary containing user information
        """
        # Convert datetime objects to strings for JSON serialization
        serializable_data = self._make_serializable(user_data)
        
        st.session_state[self.session_key] = serializable_data
        st.session_state[self.activity_key] = datetime.now()
        
        # Store additional session metadata
        st.session_state['session_start'] = datetime.now()
        st.session_state['user_id'] = user_data.get('id')
        st.session_state['user_type'] = user_data.get('user_type')
        st.session_state['username'] = user_data.get('username')
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """
        Get current user session data
        
        Returns:
            User data dictionary or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        
        return st.session_state[self.session_key]
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated
        
        Returns:
            True if user is authenticated and session is valid, False otherwise
        """
        session_data = st.session_state.get(self.session_key)
        
        if not session_data:
            return False
        
        # Check session validity
        if not SessionValidator.is_session_valid(session_data):
            self.clear_session()
            return False
        
        # Check activity timeout
        last_activity = st.session_state.get(self.activity_key)
        if last_activity:
            if datetime.now() - last_activity > timedelta(minutes=AppConfig.SESSION_TIMEOUT_MINUTES):
                self.clear_session()
                return False
        
        # Update last activity
        st.session_state[self.activity_key] = datetime.now()
        return True
    
    def clear_session(self) -> None:
        """
        Clear all session data
        """
        # Clear main session data
        st.session_state[self.session_key] = None
        st.session_state[self.activity_key] = None
        
        # Clear additional session metadata
        session_keys_to_clear = [
            'session_start',
            'user_id',
            'user_type',
            'username',
            'current_audit_id',
            'selected_documents',
            'upload_progress'
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_user_id(self) -> Optional[int]:
        """
        Get current user's ID
        
        Returns:
            User ID or None if not authenticated
        """
        user_data = self.get_user_data()
        return user_data.get('id') if user_data else None
    
    def get_user_type(self) -> Optional[str]:
        """
        Get current user's type
        
        Returns:
            User type ('auditor' or 'auditee') or None if not authenticated
        """
        user_data = self.get_user_data()
        return user_data.get('user_type') if user_data else None
    
    def get_username(self) -> Optional[str]:
        """
        Get current user's username
        
        Returns:
            Username or None if not authenticated
        """
        user_data = self.get_user_data()
        return user_data.get('username') if user_data else None
    
    def get_user_department(self) -> Optional[str]:
        """
        Get current user's department
        
        Returns:
            Department name or None if not available
        """
        user_data = self.get_user_data()
        return user_data.get('department') if user_data else None
    
    def get_session_duration(self) -> Optional[timedelta]:
        """
        Get current session duration
        
        Returns:
            Session duration as timedelta or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        
        session_start = st.session_state.get('session_start')
        if session_start:
            return datetime.now() - session_start
        
        return None
    
    def get_last_activity(self) -> Optional[datetime]:
        """
        Get timestamp of last user activity
        
        Returns:
            Last activity datetime or None if not available
        """
        return st.session_state.get(self.activity_key)
    
    def update_activity(self) -> None:
        """
        Update last activity timestamp
        """
        st.session_state[self.activity_key] = datetime.now()
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has a specific permission
        
        Args:
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        user_data = self.get_user_data()
        if not user_data:
            return False
        
        return SessionValidator.has_permission(user_data, permission)
    
    def set_current_audit(self, audit_id: int) -> None:
        """
        Set the currently selected audit ID
        
        Args:
            audit_id: ID of the audit to set as current
        """
        st.session_state['current_audit_id'] = audit_id
    
    def get_current_audit(self) -> Optional[int]:
        """
        Get the currently selected audit ID
        
        Returns:
            Current audit ID or None if not set
        """
        return st.session_state.get('current_audit_id')
    
    def set_selected_documents(self, document_ids: list) -> None:
        """
        Set list of selected document IDs
        
        Args:
            document_ids: List of document IDs
        """
        st.session_state['selected_documents'] = document_ids
    
    def get_selected_documents(self) -> list:
        """
        Get list of selected document IDs
        
        Returns:
            List of selected document IDs
        """
        return st.session_state.get('selected_documents', [])
    
    def set_upload_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Set file upload progress data
        
        Args:
            progress_data: Dictionary containing upload progress information
        """
        st.session_state['upload_progress'] = progress_data
    
    def get_upload_progress(self) -> Optional[Dict[str, Any]]:
        """
        Get file upload progress data
        
        Returns:
            Upload progress dictionary or None if not available
        """
        return st.session_state.get('upload_progress')
    
    def clear_upload_progress(self) -> None:
        """
        Clear file upload progress data
        """
        if 'upload_progress' in st.session_state:
            del st.session_state['upload_progress']
    
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert data to JSON-serializable format
        
        Args:
            data: Dictionary that may contain non-serializable objects
            
        Returns:
            Dictionary with serializable values
        """
        serializable_data = {}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                serializable_data[key] = value.isoformat()
            elif isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serializable_data[key] = value
            else:
                # Convert other types to string
                serializable_data[key] = str(value)
        
        return serializable_data
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get comprehensive session information for debugging
        
        Returns:
            Dictionary containing session information
        """
        if not self.is_authenticated():
            return {'authenticated': False}
        
        user_data = self.get_user_data()
        session_duration = self.get_session_duration()
        
        return {
            'authenticated': True,
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'user_type': user_data.get('user_type'),
            'department': user_data.get('department'),
            'session_start': st.session_state.get('session_start'),
            'last_activity': self.get_last_activity(),
            'session_duration': str(session_duration) if session_duration else None,
            'current_audit_id': self.get_current_audit(),
            'selected_documents_count': len(self.get_selected_documents())
        }
