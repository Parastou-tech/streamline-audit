"""
Auditee Dashboard for Cal Poly SLO Audit Management System

This module provides the interface for auditees to upload documents,
view audit requests, and track submission status.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

from config.settings import AppConfig
from utils.database_manager import DatabaseManager
from utils.session_manager import SessionManager
from services.file_handler import FileHandler

class AuditeeDashboard:
    """
    Main dashboard interface for auditees
    """
    
    def __init__(self):
        """
        Initialize the auditee dashboard
        """
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager()
        self.file_handler = FileHandler()
    
    def render(self):
        """
        Render the complete auditee dashboard
        """
        st.title("📤 Auditee Dashboard")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 My Audits", 
            "📤 Upload Documents", 
            "📊 Submission Status", 
            "📬 Notifications"
        ])
        
        with tab1:
            self._render_my_audits()
        
        with tab2:
            self._render_upload_documents()
        
        with tab3:
            self._render_submission_status()
        
        with tab4:
            self._render_notifications()
    
    def _render_my_audits(self):
        """
        Render the section showing audits assigned to this user
        """
        st.header("📋 My Assigned Audits")
        
        user_department = self.session_manager.get_user_department()
        audits = self._get_department_audits(user_department)
        
        if not audits:
            st.info("No audits currently assigned to your department.")
            return
        
        # Display audit cards
        for audit in audits:
            with st.expander(f"🔍 {audit['audit_name']} - Due: {audit.get('due_date', 'Not set')}"):
                self._render_audit_card(audit)
    
    def _render_upload_documents(self):
        """
        Render the document upload section
        """
        st.header("📤 Upload Documents")
        
        # Select audit to upload for
        user_department = self.session_manager.get_user_department()
        audits = self._get_department_audits(user_department)
        
        if not audits:
            st.warning("No active audits found for your department.")
            return
        
        # Audit selection
        audit_options = {f"{audit['audit_name']} ({audit['auditor_name']})": audit['id'] 
                        for audit in audits}
        
        selected_audit_name = st.selectbox("Select Audit", list(audit_options.keys()))
        selected_audit_id = audit_options[selected_audit_name]
        
        # Get selected audit details
        selected_audit = next(audit for audit in audits if audit['id'] == selected_audit_id)
        
        # Display audit requirements
        st.subheader("📋 Document Requirements")
        st.info(selected_audit['document_requests'])
        
        # File upload section
        st.subheader("📁 Upload Files")
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['pdf', 'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'],
            accept_multiple_files=True,
            help=f"Maximum file size: {AppConfig.MAX_FILE_SIZE_MB}MB per file"
        )
        
        if uploaded_files:
            # Display file information
            st.subheader("📄 Selected Files")
            
            valid_files = []
            for file in uploaded_files:
                file_size_mb = file.size / (1024 * 1024)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{file.name}**")
                
                with col2:
                    st.write(f"Size: {file_size_mb:.2f} MB")
                
                with col3:
                    st.write(f"Type: {file.type}")
                
                with col4:
                    if file_size_mb <= AppConfig.MAX_FILE_SIZE_MB:
                        st.success("✅ Valid")
                        valid_files.append(file)
                    else:
                        st.error("❌ Too large")
            
            # Upload button
            if valid_files:
                if st.button("🚀 Upload Files", use_container_width=True):
                    self._upload_files(valid_files, selected_audit_id)
            else:
                st.error("No valid files to upload. Please check file sizes and types.")
    
    def _render_submission_status(self):
        """
        Render the submission status tracking section
        """
        st.header("📊 Document Submission Status")
        
        user_id = self.session_manager.get_user_id()
        documents = self._get_user_documents(user_id)
        
        if not documents:
            st.info("No documents uploaded yet.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_docs = len(documents)
        pending_docs = len([d for d in documents if d['status'] == 'Pending'])
        approved_docs = len([d for d in documents if d['status'] in ['Compliant', 'Approved']])
        rejected_docs = len([d for d in documents if d['status'] == 'Non-Compliant'])
        
        with col1:
            st.metric("Total Uploaded", total_docs)
        
        with col2:
            st.metric("Pending Review", pending_docs)
        
        with col3:
            st.metric("Approved", approved_docs)
        
        with col4:
            st.metric("Need Revision", rejected_docs)
        
        # Document list
        st.subheader("📄 Document Details")
        
        # Create DataFrame for better display
        df_data = []
        for doc in documents:
            df_data.append({
                'File Name': doc['original_filename'],
                'Audit': doc['audit_name'],
                'Upload Date': doc['upload_date'],
                'Status': doc['status'],
                'Notes': doc.get('compliance_notes', 'No notes')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
    
    def _render_notifications(self):
        """
        Render the notifications section
        """
        st.header("📬 Notifications")
        
        user_id = self.session_manager.get_user_id()
        notifications = self._get_user_notifications(user_id)
        
        if not notifications:
            st.info("No notifications at this time.")
            return
        
        # Unread notifications count
        unread_count = len([n for n in notifications if not n['is_read']])
        if unread_count > 0:
            st.warning(f"You have {unread_count} unread notifications")
        
        # Display notifications
        for notification in notifications:
            with st.expander(
                f"{'🔴' if not notification['is_read'] else '✅'} "
                f"{notification['notification_type']} - {notification['created_at']}"
            ):
                st.write(notification['message'])
                
                if notification.get('sender_name'):
                    st.write(f"**From:** {notification['sender_name']}")
                
                if notification.get('audit_name'):
                    st.write(f"**Related Audit:** {notification['audit_name']}")
                
                if not notification['is_read']:
                    if st.button(f"Mark as Read", key=f"read_{notification['id']}"):
                        self._mark_notification_read(notification['id'])
                        st.rerun()
    
    def _get_department_audits(self, department: str) -> List[Dict]:
        """
        Get all audits for the user's department
        """
        query = '''
            SELECT a.*, u.name as auditor_name
            FROM audits a
            JOIN users u ON a.auditor_id = u.id
            WHERE a.target_department = ? AND a.status = 'Active'
            ORDER BY a.created_at DESC
        '''
        return self.db_manager.fetch_all(query, (department,))
    
    def _render_audit_card(self, audit: Dict):
        """
        Render a detailed audit card
        """
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Auditor:** {audit['auditor_name']}")
            st.write(f"**Category:** {audit['audit_category']}")
            st.write(f"**Status:** {audit['status']}")
        
        with col2:
            st.write(f"**Created:** {audit['created_at']}")
            st.write(f"**Due Date:** {audit.get('due_date', 'Not specified')}")
        
        st.write(f"**Description:**")
        st.write(audit['description'])
        
        st.write(f"**Required Documents:**")
        st.info(audit['document_requests'])
        
        # Show uploaded documents for this audit
        user_id = self.session_manager.get_user_id()
        audit_docs = self._get_audit_documents(audit['id'], user_id)
        
        if audit_docs:
            st.write(f"**Your Uploaded Documents ({len(audit_docs)}):**")
            for doc in audit_docs:
                status_color = {
                    'Pending': '🟡',
                    'Under Review': '🔵',
                    'Compliant': '🟢',
                    'Non-Compliant': '🔴',
                    'Approved': '✅'
                }.get(doc['status'], '⚪')
                
                st.write(f"{status_color} {doc['original_filename']} - {doc['status']}")
    
    def _upload_files(self, files: List, audit_id: int) -> None:
        """
        Handle file upload process
        """
        user_id = self.session_manager.get_user_id()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_uploads = 0
        total_files = len(files)
        
        for i, file in enumerate(files):
            try:
                status_text.text(f"Uploading {file.name}...")
                
                # Save file and get metadata
                file_info = self.file_handler.save_uploaded_file(file, audit_id, user_id)
                
                if file_info:
                    # Save to database
                    self._save_document_record(file_info, audit_id, user_id)
                    successful_uploads += 1
                
                progress_bar.progress((i + 1) / total_files)
                
            except Exception as e:
                st.error(f"Error uploading {file.name}: {str(e)}")
        
        status_text.text("Upload complete!")
        
        if successful_uploads == total_files:
            st.success(f"✅ Successfully uploaded {successful_uploads} files!")
        else:
            st.warning(f"⚠️ Uploaded {successful_uploads} out of {total_files} files.")
        
        # Clear progress indicators after a moment
        import time
        time.sleep(2)
        progress_bar.empty()
        status_text.empty()
    
    def _save_document_record(self, file_info: Dict, audit_id: int, user_id: int) -> bool:
        """
        Save document record to database
        """
        try:
            query = '''
                INSERT INTO documents (audit_id, uploader_id, filename, original_filename,
                                     file_type, file_size, s3_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            
            cursor = self.db_manager.execute_query(
                query, (
                    audit_id, user_id, file_info['filename'], file_info['original_filename'],
                    file_info['file_type'], file_info['file_size'], file_info.get('s3_key')
                )
            )
            
            return cursor is not None
            
        except Exception as e:
            st.error(f"Error saving document record: {str(e)}")
            return False
    
    def _get_user_documents(self, user_id: int) -> List[Dict]:
        """
        Get all documents uploaded by the user
        """
        query = '''
            SELECT d.*, a.audit_name
            FROM documents d
            JOIN audits a ON d.audit_id = a.id
            WHERE d.uploader_id = ?
            ORDER BY d.upload_date DESC
        '''
        return self.db_manager.fetch_all(query, (user_id,))
    
    def _get_audit_documents(self, audit_id: int, user_id: int) -> List[Dict]:
        """
        Get documents uploaded by user for specific audit
        """
        query = '''
            SELECT * FROM documents
            WHERE audit_id = ? AND uploader_id = ?
            ORDER BY upload_date DESC
        '''
        return self.db_manager.fetch_all(query, (audit_id, user_id))
    
    def _get_user_notifications(self, user_id: int) -> List[Dict]:
        """
        Get notifications for the user
        """
        query = '''
            SELECT n.*, u.name as sender_name, a.audit_name
            FROM notifications n
            LEFT JOIN users u ON n.sender_id = u.id
            LEFT JOIN audits a ON n.audit_id = a.id
            WHERE n.recipient_id = ?
            ORDER BY n.created_at DESC
        '''
        return self.db_manager.fetch_all(query, (user_id,))
    
    def _mark_notification_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read
        """
        try:
            query = 'UPDATE notifications SET is_read = 1 WHERE id = ?'
            cursor = self.db_manager.execute_query(query, (notification_id,))
            return cursor is not None
            
        except Exception as e:
            st.error(f"Error marking notification as read: {str(e)}")
            return False
