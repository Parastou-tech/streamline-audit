"""
Setup Script for Cal Poly SLO Audit Management System

This script initializes the database and creates necessary directories
for the audit management system.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import AppConfig, DatabaseConfig
from utils.database_manager import DatabaseManager
from auth.authentication import AuthenticationManager

def create_directories():
    """Create necessary directories for the application"""
    directories = [
        project_root / "data",
        project_root / "uploads",
        project_root / "uploads" / "temp",
        project_root / "uploads" / "processed",
        project_root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_database():
    """Initialize the database with required tables"""
    try:
        db_manager = DatabaseManager()
        print("✅ Database initialized successfully")
        
        # Create default users for testing
        auth_manager = AuthenticationManager()
        print("✅ Authentication system initialized")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False
    
    return True

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = project_root / ".env"
    template_file = project_root / ".env.template"
    
    if not env_file.exists() and template_file.exists():
        import shutil
        shutil.copy(template_file, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual configuration values")
    else:
        print("ℹ️  .env file already exists")

def main():
    """Main setup function"""
    print("🏛️ Cal Poly SLO Audit Management System Setup")
    print("=" * 50)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create environment file
    print("\n🔧 Setting up environment...")
    create_env_file()
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    if initialize_database():
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit the .env file with your configuration")
        print("2. Run: streamlit run main.py")
        print("3. Login with default credentials:")
        print("   - Auditor: username=auditor1, password=password123")
        print("   - Auditee: username=auditee1, password=password123")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
