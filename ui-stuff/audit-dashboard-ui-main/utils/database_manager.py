"""
Database Manager for Cal Poly SLO Audit Management System

This module handles all database operations including connection management,
query execution, and database initialization.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st

from config.settings import AppConfig, DatabaseConfig

class DatabaseManager:
    """
    Manages database connections and operations for the audit system
    """
    
    def __init__(self):
        """
        Initialize database manager and ensure database exists
        """
        self.db_path = AppConfig.DATABASE_PATH
        self._ensure_database_directory()
        self._initialize_database()
    
    def _ensure_database_directory(self) -> None:
        """
        Ensure the database directory exists
        """
        db_dir = self.db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self) -> None:
        """
        Initialize database with required tables if they don't exist
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Create all tables
                for table_name, create_sql in DatabaseConfig.TABLES.items():
                    cursor.execute(create_sql)
                
                conn.commit()
                
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with row factory
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Cursor]:
        """
        Execute a query that modifies data (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Cursor object or None if error occurred
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
                
        except Exception as e:
            st.error(f"Database query error: {str(e)}")
            return None
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from the database
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Dictionary representing the row or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            st.error(f"Database fetch error: {str(e)}")
            return None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Fetch all rows from a query
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of dictionaries representing the rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            st.error(f"Database fetch error: {str(e)}")
            return []
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> bool:
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database batch execution error: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's structure
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query)
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        query = '''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        '''
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_row_count(self, table_name: str, where_clause: str = "", params: Tuple = ()) -> int:
        """
        Get the number of rows in a table
        
        Args:
            table_name: Name of the table
            where_clause: Optional WHERE clause (without WHERE keyword)
            params: Parameters for WHERE clause
            
        Returns:
            Number of rows
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.fetch_one(query, params)
        return result['count'] if result else 0
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Path where backup should be saved
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
            
        except Exception as e:
            st.error(f"Database backup error: {str(e)}")
            return False
    
    def vacuum_database(self) -> bool:
        """
        Optimize database by running VACUUM command
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database vacuum error: {str(e)}")
            return False

class AuditQueries:
    """
    Predefined queries for audit-related operations
    """
    
    @staticmethod
    def get_active_audits_for_auditor(auditor_id: int) -> str:
        """Get all active audits for a specific auditor"""
        return '''
            SELECT a.*, u.name as auditor_name
            FROM audits a
            JOIN users u ON a.auditor_id = u.id
            WHERE a.auditor_id = ? AND a.status = 'Active'
            ORDER BY a.created_at DESC
        '''
    
    @staticmethod
    def get_audits_for_department(department: str) -> str:
        """Get all audits targeting a specific department"""
        return '''
            SELECT a.*, u.name as auditor_name
            FROM audits a
            JOIN users u ON a.auditor_id = u.id
            WHERE a.target_department = ?
            ORDER BY a.created_at DESC
        '''
    
    @staticmethod
    def get_documents_for_audit(audit_id: int) -> str:
        """Get all documents for a specific audit"""
        return '''
            SELECT d.*, u.name as uploader_name
            FROM documents d
            JOIN users u ON d.uploader_id = u.id
            WHERE d.audit_id = ?
            ORDER BY d.upload_date DESC
        '''
    
    @staticmethod
    def get_pending_documents() -> str:
        """Get all documents with pending status"""
        return '''
            SELECT d.*, a.audit_name, u.name as uploader_name
            FROM documents d
            JOIN audits a ON d.audit_id = a.id
            JOIN users u ON d.uploader_id = u.id
            WHERE d.status = 'Pending'
            ORDER BY d.upload_date ASC
        '''
    
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False) -> str:
        """Get notifications for a specific user"""
        query = '''
            SELECT n.*, u.name as sender_name, a.audit_name
            FROM notifications n
            LEFT JOIN users u ON n.sender_id = u.id
            LEFT JOIN audits a ON n.audit_id = a.id
            WHERE n.recipient_id = ?
        '''
        
        if unread_only:
            query += " AND n.is_read = 0"
        
        query += " ORDER BY n.created_at DESC"
        return query
    
    @staticmethod
    def get_audit_statistics() -> str:
        """Get overall audit statistics"""
        return '''
            SELECT 
                COUNT(*) as total_audits,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_audits,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_audits,
                COUNT(DISTINCT target_department) as departments_audited
            FROM audits
        '''
    
    @staticmethod
    def get_document_statistics() -> str:
        """Get document statistics"""
        return '''
            SELECT 
                COUNT(*) as total_documents,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_documents,
                SUM(CASE WHEN status = 'Compliant' THEN 1 ELSE 0 END) as compliant_documents,
                SUM(CASE WHEN status = 'Non-Compliant' THEN 1 ELSE 0 END) as non_compliant_documents,
                AVG(file_size) as avg_file_size
            FROM documents
        '''
