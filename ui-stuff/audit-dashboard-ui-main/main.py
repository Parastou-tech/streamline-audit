"""
Cal Poly SLO Audit Management System
Main Streamlit Application Entry Point

This is the main entry point for the audit management system.
It handles user authentication and routes users to appropriate dashboards.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import custom modules
from config.settings import AppConfig
from auth.authentication import AuthenticationManager
from dashboards.auditor_dashboard import AuditorDashboard
from dashboards.auditee_dashboard import AuditeeDashboard
from utils.session_manager import SessionManager

# Configure Streamlit page
st.set_page_config(
    page_title="Cal Poly SLO Audit Management System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """
    Main application function that handles routing and authentication
    """
    # Initialize session manager
    session_manager = SessionManager()
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager()
    
    # Custom CSS for Cal Poly branding
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e3d 0%, #2d5a47 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #b8d4c8;
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .stButton > button {
        background-color: #1f4e3d;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2d5a47;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Cal Poly SLO Audit Management System</h1>
        <p>Secure Document Management and Compliance Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not session_manager.is_authenticated():
        show_login_page(auth_manager, session_manager)
    else:
        show_dashboard(session_manager)

def show_login_page(auth_manager, session_manager):
    """
    Display the login page for user authentication
    
    Args:
        auth_manager: AuthenticationManager instance
        session_manager: SessionManager instance
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 User Authentication")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your Cal Poly username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            user_type = st.selectbox("User Type", ["Auditor", "Auditee"])
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    # Authenticate user
                    user_data = auth_manager.authenticate_user(username, password, user_type.lower())
                    
                    if user_data:
                        # Set session data
                        session_manager.set_user_session(user_data)
                        st.success(f"Welcome, {user_data['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.error("Please enter both username and password.")
        
        # Information section
        st.markdown("---")
        st.markdown("""
        **System Information:**
        - **Auditors**: Access audit management, document review, and compliance tracking
        - **Auditees**: Upload requested documents and track submission status
        - **Security**: All data is encrypted and stored securely
        - **Support**: Contact IT Support for login issues
        """)

def show_dashboard(session_manager):
    """
    Display the appropriate dashboard based on user type
    
    Args:
        session_manager: SessionManager instance
    """
    user_data = session_manager.get_user_data()
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown(f"### Welcome, {user_data['name']}")
        st.markdown(f"**Role:** {user_data['user_type'].title()}")
        st.markdown(f"**Department:** {user_data.get('department', 'N/A')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            session_manager.clear_session()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**System Status:** ✅ Online")
        st.markdown("**Last Updated:** " + str(session_manager.get_last_activity()))
    
    # Route to appropriate dashboard
    if user_data['user_type'] == 'auditor':
        auditor_dashboard = AuditorDashboard()
        auditor_dashboard.render()
    elif user_data['user_type'] == 'auditee':
        auditee_dashboard = AuditeeDashboard()
        auditee_dashboard.render()
    else:
        st.error("Invalid user type. Please contact system administrator.")

if __name__ == "__main__":
    main()
