"""
Configuration Settings for Cal Poly SLO Audit Management System

This module contains all configuration settings, constants, and environment variables
used throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """
    Application configuration class containing all settings and constants
    """
    
    # Application Settings
    APP_NAME = "Cal Poly SLO Audit Management System"
    APP_VERSION = "1.0.0"
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Database Settings
    DATABASE_PATH = Path(__file__).parent.parent / "data" / "audit_system.db"
    
    # File Upload Settings
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_FILE_TYPES = {
        'pdf': ['application/pdf'],
        'excel': [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        'csv': ['text/csv'],
        'images': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
        'word': [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
    }
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "calpoly-audit-documents")
    S3_UPLOAD_PREFIX = "uploads/"
    S3_PROCESSED_PREFIX = "processed/"
    
    # Textract Configuration
    TEXTRACT_REGION = AWS_REGION
    
    # Claude AI Configuration
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL = "claude-3-sonnet-20240229"
    
    # Email Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.calpoly.edu")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "audit-system@calpoly.edu")
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    PASSWORD_MIN_LENGTH = 8
    
    # Cal Poly Departments
    DEPARTMENTS = [
        "Academic Affairs",
        "Administration and Finance",
        "Student Affairs",
        "University Advancement",
        "Research and Economic Development",
        "Information Technology Services",
        "Human Resources",
        "Facilities Management",
        "Library Services",
        "Athletics",
        "College of Agriculture, Food and Environmental Sciences",
        "College of Architecture and Environmental Design",
        "College of Engineering",
        "College of Liberal Arts",
        "College of Science and Mathematics",
        "Orfalea College of Business"
    ]
    
    # Audit Categories
    AUDIT_CATEGORIES = [
        "Financial Compliance",
        "IT Security",
        "Research Compliance",
        "Student Records",
        "HR Policies",
        "Facilities and Safety",
        "Academic Programs",
        "Grant Management",
        "Procurement",
        "Data Privacy"
    ]
    
    # Document Status Options
    DOCUMENT_STATUS = [
        "Pending",
        "Under Review",
        "Compliant",
        "Non-Compliant",
        "Needs Revision",
        "Approved"
    ]
    
    # Compliance Flags
    COMPLIANCE_FLAGS = [
        "Missing Required Information",
        "Incorrect Format",
        "Outdated Document",
        "Incomplete Data",
        "Security Concern",
        "Policy Violation",
        "Requires Additional Documentation"
    ]

class DatabaseConfig:
    """
    Database configuration and table schemas
    """
    
    # Table creation SQL statements
    TABLES = {
        'users': '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                user_type TEXT NOT NULL,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''',
        
        'audits': '''
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_name TEXT NOT NULL,
                auditor_id INTEGER NOT NULL,
                target_department TEXT NOT NULL,
                audit_category TEXT NOT NULL,
                description TEXT,
                document_requests TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                FOREIGN KEY (auditor_id) REFERENCES users (id)
            )
        ''',
        
        'documents': '''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                uploader_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                s3_key TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Pending',
                compliance_notes TEXT,
                ai_analysis TEXT,
                textract_data TEXT,
                FOREIGN KEY (audit_id) REFERENCES audits (id),
                FOREIGN KEY (uploader_id) REFERENCES users (id)
            )
        ''',
        
        'notifications': '''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                sender_id INTEGER,
                audit_id INTEGER,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES users (id),
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (audit_id) REFERENCES audits (id)
            )
        ''',
        
        'audit_assignments': '''
            CREATE TABLE IF NOT EXISTS audit_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                auditee_id INTEGER NOT NULL,
                assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Assigned',
                FOREIGN KEY (audit_id) REFERENCES audits (id),
                FOREIGN KEY (auditee_id) REFERENCES users (id)
            )
        '''
    }

# Environment file template
ENV_TEMPLATE = """
# Cal Poly SLO Audit Management System Environment Variables
# Copy this file to .env and fill in your actual values

# Debug Mode
DEBUG_MODE=False

# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
S3_BUCKET_NAME=calpoly-audit-documents

# Claude AI Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Email Configuration
SMTP_SERVER=smtp.calpoly.edu
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=audit-system@calpoly.edu

# Security
SECRET_KEY=your-very-secure-secret-key-change-this
SESSION_TIMEOUT_MINUTES=60
"""
