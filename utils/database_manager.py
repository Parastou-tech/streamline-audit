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
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Cursor]:
        """
        Execute a query that modifies data (INSERT, UPDATE, DELETE)
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
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database
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
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.fetch_one(query, params)
        return result['count'] if result else 0


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
    def get_documents_for_audit(audit_id: int) -> str:
        """Get all documents for a specific audit"""
        return '''
            SELECT d.*, u.name as uploader_name
            FROM documents d
            JOIN users u ON d.uploader_id = u.id
            WHERE d.audit_id = ?
            ORDER BY d.upload_date DESC
        '''