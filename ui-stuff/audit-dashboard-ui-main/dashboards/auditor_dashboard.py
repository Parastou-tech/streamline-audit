"""
Auditor Dashboard for Cal Poly SLO Audit Management System

This module provides the main interface for auditors to manage audits,
review documents, and track compliance status.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any

from config.settings import AppConfig
from utils.database_manager import DatabaseManager, AuditQueries
from utils.session_manager import SessionManager

class AuditorDashboard:
    """
    Main dashboard interface for auditors
    """
    
    def __init__(self):
        """
        Initialize the auditor dashboard
        """
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager()
    
    def render(self):
        """
        Render the complete auditor dashboard
        """
        st.title("🔍 Auditor Dashboard")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview", 
            "🆕 Create Audit", 
            "📋 Manage Audits", 
            "📄 Review Documents"
        ])
        
        with tab1:
            self._render_overview()
        
        with tab2:
            self._render_create_audit()
        
        with tab3:
            self._render_manage_audits()
        
        with tab4:
            self._render_review_documents()
    
    def _render_overview(self):
        """
        Render the overview section with statistics and recent activity
        """
        st.header("📊 Audit Overview")
        
        # Get current user
        user_id = self.session_manager.get_user_id()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active_audits = self._get_active_audits_count(user_id)
            st.metric("Active Audits", active_audits)
        
        with col2:
            pending_docs = self._get_pending_documents_count()
            st.metric("Pending Documents", pending_docs)
        
        with col3:
            total_audits = self._get_total_audits_count(user_id)
            st.metric("Total Audits", total_audits)
        
        with col4:
            compliance_rate = self._get_compliance_rate()
            st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        recent_audits = self._get_recent_audits(user_id, limit=5)
        
        if recent_audits:
            df = pd.DataFrame(recent_audits)
            st.dataframe(df[['audit_name', 'target_department', 'status', 'created_at']], 
                        use_container_width=True)
        else:
            st.info("No recent audit activity")
    
    def _render_create_audit(self):
        """
        Render the create new audit section
        """
        st.header("🆕 Create New Audit")
        
        with st.form("create_audit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                audit_name = st.text_input("Audit Name*", 
                                         placeholder="e.g., Q4 2024 Financial Review")
                target_department = st.selectbox("Target Department*", 
                                               AppConfig.DEPARTMENTS)
                audit_category = st.selectbox("Audit Category*", 
                                            AppConfig.AUDIT_CATEGORIES)
            
            with col2:
                due_date = st.date_input("Due Date", 
                                       min_value=date.today())
                priority = st.selectbox("Priority", 
                                      ["Low", "Medium", "High", "Critical"])
            
            description = st.text_area("Audit Description*", 
                                     placeholder="Describe the purpose and scope of this audit...")
            
            document_requests = st.text_area("Document Requests*", 
                                           placeholder="List the specific documents needed for this audit...")
            
            submitted = st.form_submit_button("Create Audit", use_container_width=True)
            
            if submitted:
                if audit_name and target_department and description and document_requests:
                    success = self._create_audit(
                        audit_name, target_department, audit_category,
                        description, document_requests, due_date
                    )
                    
                    if success:
                        st.success("✅ Audit created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create audit. Please try again.")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    def _render_manage_audits(self):
        """
        Render the manage existing audits section
        """
        st.header("📋 Manage Audits")
        
        user_id = self.session_manager.get_user_id()
        audits = self._get_user_audits(user_id)
        
        if not audits:
            st.info("No audits found. Create your first audit in the 'Create Audit' tab.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All", "Active", "Completed", "On Hold"])
        
        with col2:
            department_filter = st.selectbox("Filter by Department", 
                                           ["All"] + AppConfig.DEPARTMENTS)
        
        with col3:
            category_filter = st.selectbox("Filter by Category", 
                                         ["All"] + AppConfig.AUDIT_CATEGORIES)
        
        # Apply filters
        filtered_audits = self._filter_audits(audits, status_filter, 
                                            department_filter, category_filter)
        
        # Display audits
        for audit in filtered_audits:
            with st.expander(f"🔍 {audit['audit_name']} - {audit['status']}"):
                self._render_audit_details(audit)
    
    def _render_review_documents(self):
        """
        Render the document review section
        """
        st.header("📄 Review Documents")
        
        # Get pending documents
        pending_docs = self._get_pending_documents()
        
        if not pending_docs:
            st.info("No documents pending review.")
            return
        
        st.subheader(f"📋 {len(pending_docs)} Documents Pending Review")
        
        for doc in pending_docs:
            with st.expander(f"📄 {doc['original_filename']} - {doc['audit_name']}"):
                self._render_document_review(doc)
    
    def _create_audit(self, audit_name: str, target_department: str, 
                     audit_category: str, description: str, 
                     document_requests: str, due_date: date) -> bool:
        """
        Create a new audit in the database
        """
        try:
            user_id = self.session_manager.get_user_id()
            
            query = '''
                INSERT INTO audits (audit_name, auditor_id, target_department, 
                                  audit_category, description, document_requests, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            
            cursor = self.db_manager.execute_query(
                query, (audit_name, user_id, target_department, audit_category,
                       description, document_requests, due_date)
            )
            
            return cursor is not None
            
        except Exception as e:
            st.error(f"Error creating audit: {str(e)}")
            return False
    
    def _get_active_audits_count(self, user_id: int) -> int:
        """Get count of active audits for user"""
        return self.db_manager.get_row_count(
            'audits', 
            'auditor_id = ? AND status = ?', 
            (user_id, 'Active')
        )
    
    def _get_pending_documents_count(self) -> int:
        """Get count of pending documents"""
        return self.db_manager.get_row_count(
            'documents', 
            'status = ?', 
            ('Pending',)
        )
    
    def _get_total_audits_count(self, user_id: int) -> int:
        """Get total audits count for user"""
        return self.db_manager.get_row_count(
            'audits', 
            'auditor_id = ?', 
            (user_id,)
        )
    
    def _get_compliance_rate(self) -> float:
        """Calculate overall compliance rate"""
        total_docs = self.db_manager.get_row_count('documents')
        if total_docs == 0:
            return 0.0
        
        compliant_docs = self.db_manager.get_row_count(
            'documents', 
            'status = ?', 
            ('Compliant',)
        )
        
        return (compliant_docs / total_docs) * 100
    
    def _get_recent_audits(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent audits for user"""
        query = '''
            SELECT * FROM audits 
            WHERE auditor_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        return self.db_manager.fetch_all(query, (user_id, limit))
    
    def _get_user_audits(self, user_id: int) -> List[Dict]:
        """Get all audits for user"""
        query = AuditQueries.get_active_audits_for_auditor(user_id)
        return self.db_manager.fetch_all(query, (user_id,))
    
    def _filter_audits(self, audits: List[Dict], status_filter: str,
                      department_filter: str, category_filter: str) -> List[Dict]:
        """Apply filters to audit list"""
        filtered = audits
        
        if status_filter != "All":
            filtered = [a for a in filtered if a['status'] == status_filter]
        
        if department_filter != "All":
            filtered = [a for a in filtered if a['target_department'] == department_filter]
        
        if category_filter != "All":
            filtered = [a for a in filtered if a['audit_category'] == category_filter]
        
        return filtered
    
    def _render_audit_details(self, audit: Dict):
        """Render detailed view of an audit"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Department:** {audit['target_department']}")
            st.write(f"**Category:** {audit['audit_category']}")
            st.write(f"**Status:** {audit['status']}")
        
        with col2:
            st.write(f"**Created:** {audit['created_at']}")
            st.write(f"**Due Date:** {audit.get('due_date', 'Not set')}")
        
        st.write(f"**Description:** {audit['description']}")
        st.write(f"**Document Requests:** {audit['document_requests']}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"View Documents", key=f"view_docs_{audit['id']}"):
                self.session_manager.set_current_audit(audit['id'])
        
        with col2:
            if st.button(f"Send Notification", key=f"notify_{audit['id']}"):
                st.info("Notification feature coming soon!")
        
        with col3:
            if st.button(f"Update Status", key=f"update_{audit['id']}"):
                st.info("Status update feature coming soon!")
    
    def _get_pending_documents(self) -> List[Dict]:
        """Get all pending documents"""
        query = AuditQueries.get_pending_documents()
        return self.db_manager.fetch_all(query)
    
    def _render_document_review(self, doc: Dict):
        """Render document review interface"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Uploader:** {doc['uploader_name']}")
            st.write(f"**File Type:** {doc['file_type']}")
            st.write(f"**Size:** {doc['file_size']} bytes")
            st.write(f"**Uploaded:** {doc['upload_date']}")
        
        with col2:
            new_status = st.selectbox(
                "Update Status",
                AppConfig.DOCUMENT_STATUS,
                key=f"status_{doc['id']}"
            )
            
            compliance_notes = st.text_area(
                "Compliance Notes",
                value=doc.get('compliance_notes', ''),
                key=f"notes_{doc['id']}"
            )
        
        if st.button(f"Update Document", key=f"update_doc_{doc['id']}"):
            self._update_document_status(doc['id'], new_status, compliance_notes)
            st.success("Document updated successfully!")
            st.rerun()
    
    def _update_document_status(self, doc_id: int, status: str, notes: str) -> bool:
        """Update document status and notes"""
        try:
            query = '''
                UPDATE documents 
                SET status = ?, compliance_notes = ? 
                WHERE id = ?
            '''
            
            cursor = self.db_manager.execute_query(query, (status, notes, doc_id))
            return cursor is not None
            
        except Exception as e:
            st.error(f"Error updating document: {str(e)}")
            return False
