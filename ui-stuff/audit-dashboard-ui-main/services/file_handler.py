"""
File Handler Service for Cal Poly SLO Audit Management System

This module handles file upload, storage, validation, and processing
for the audit management system.
"""

import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import streamlit as st

from config.settings import AppConfig

class FileHandler:
    """
    Handles file operations including upload, validation, and storage
    """
    
    def __init__(self):
        """
        Initialize file handler with storage configuration
        """
        self.upload_dir = Path(__file__).parent.parent / "uploads"
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.upload_dir / "temp").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
    
    def save_uploaded_file(self, uploaded_file, audit_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Save an uploaded file and return file information
        
        Args:
            uploaded_file: Streamlit uploaded file object
            audit_id: ID of the audit this file belongs to
            user_id: ID of the user uploading the file
            
        Returns:
            Dictionary with file information or None if failed
        """
        try:
            # Validate file
            if not self._validate_file(uploaded_file):
                return None
            
            # Generate unique filename
            file_extension = self._get_file_extension(uploaded_file.name)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create file path
            file_path = self.upload_dir / "temp" / unique_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            
            # Prepare file information
            file_info = {
                'filename': unique_filename,
                'original_filename': uploaded_file.name,
                'file_type': uploaded_file.type,
                'file_size': uploaded_file.size,
                'file_path': str(file_path),
                'file_hash': file_hash,
                'audit_id': audit_id,
                'user_id': user_id,
                'upload_timestamp': datetime.now().isoformat()
            }
            
            return file_info
            
        except Exception as e:
            st.error(f"Error saving file {uploaded_file.name}: {str(e)}")
            return None
    
    def _validate_file(self, uploaded_file) -> bool:
        """
        Validate uploaded file against security and size constraints
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            True if file is valid, False otherwise
        """
        # Check file size
        if uploaded_file.size > AppConfig.MAX_FILE_SIZE_BYTES:
            st.error(f"File {uploaded_file.name} is too large. Maximum size is {AppConfig.MAX_FILE_SIZE_MB}MB.")
            return False
        
        # Check file type
        if not self._is_allowed_file_type(uploaded_file.type):
            st.error(f"File type {uploaded_file.type} is not allowed.")
            return False
        
        # Check filename for security
        if not self._is_safe_filename(uploaded_file.name):
            st.error(f"Filename {uploaded_file.name} contains invalid characters.")
            return False
        
        return True
    
    def _is_allowed_file_type(self, file_type: str) -> bool:
        """
        Check if file type is in allowed list
        
        Args:
            file_type: MIME type of the file
            
        Returns:
            True if file type is allowed, False otherwise
        """
        allowed_types = []
        for type_list in AppConfig.ALLOWED_FILE_TYPES.values():
            allowed_types.extend(type_list)
        
        return file_type in allowed_types
    
    def _is_safe_filename(self, filename: str) -> bool:
        """
        Check if filename is safe (no path traversal, etc.)
        
        Args:
            filename: Original filename
            
        Returns:
            True if filename is safe, False otherwise
        """
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for null bytes
        if '\x00' in filename:
            return False
        
        # Check filename length
        if len(filename) > 255:
            return False
        
        return True
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename
        
        Args:
            filename: Original filename
            
        Returns:
            File extension including the dot
        """
        return Path(filename).suffix.lower()
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of file for integrity checking
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a stored file
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with file information or None if not found
        """
        file_path = self.upload_dir / "temp" / filename
        
        if not file_path.exists():
            file_path = self.upload_dir / "processed" / filename
        
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        
        return {
            'filename': filename,
            'file_path': str(file_path),
            'file_size': stat.st_size,
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime)
        }
    
    def move_to_processed(self, filename: str) -> bool:
        """
        Move file from temp to processed directory
        
        Args:
            filename: Name of the file to move
            
        Returns:
            True if successful, False otherwise
        """
        try:
            temp_path = self.upload_dir / "temp" / filename
            processed_path = self.upload_dir / "processed" / filename
            
            if temp_path.exists():
                temp_path.rename(processed_path)
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error moving file to processed: {str(e)}")
            return False
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check both directories
            for directory in ["temp", "processed"]:
                file_path = self.upload_dir / directory / filename
                if file_path.exists():
                    file_path.unlink()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_content(self, filename: str) -> Optional[bytes]:
        """
        Get file content as bytes
        
        Args:
            filename: Name of the file
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            # Check both directories
            for directory in ["temp", "processed"]:
                file_path = self.upload_dir / directory / filename
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        return f.read()
            
            return None
            
        except Exception as e:
            st.error(f"Error reading file content: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up files older than specified days
        
        Args:
            days_old: Number of days after which files should be deleted
            
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for directory in ["temp", "processed"]:
                dir_path = self.upload_dir / directory
                
                for file_path in dir_path.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            st.error(f"Error during cleanup: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage information
        """
        try:
            stats = {
                'temp_files': 0,
                'processed_files': 0,
                'temp_size': 0,
                'processed_size': 0,
                'total_files': 0,
                'total_size': 0
            }
            
            # Count temp files
            temp_dir = self.upload_dir / "temp"
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    stats['temp_files'] += 1
                    stats['temp_size'] += file_path.stat().st_size
            
            # Count processed files
            processed_dir = self.upload_dir / "processed"
            for file_path in processed_dir.iterdir():
                if file_path.is_file():
                    stats['processed_files'] += 1
                    stats['processed_size'] += file_path.stat().st_size
            
            # Calculate totals
            stats['total_files'] = stats['temp_files'] + stats['processed_files']
            stats['total_size'] = stats['temp_size'] + stats['processed_size']
            
            return stats
            
        except Exception as e:
            st.error(f"Error getting storage stats: {str(e)}")
            return {}

class FileValidator:
    """
    Additional file validation utilities
    """
    
    @staticmethod
    def is_pdf(file_content: bytes) -> bool:
        """Check if file is a valid PDF"""
        return file_content.startswith(b'%PDF-')
    
    @staticmethod
    def is_image(file_content: bytes) -> bool:
        """Check if file is a valid image"""
        image_signatures = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'GIF87a',  # GIF87a
            b'GIF89a'   # GIF89a
        ]
        
        for signature in image_signatures:
            if file_content.startswith(signature):
                return True
        
        return False
    
    @staticmethod
    def is_office_document(file_content: bytes) -> bool:
        """Check if file is a Microsoft Office document"""
        # Office documents are ZIP files with specific structure
        return file_content.startswith(b'PK\x03\x04')
    
    @staticmethod
    def scan_for_malware(file_path: str) -> bool:
        """
        Placeholder for malware scanning
        In production, integrate with antivirus API
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            True if file is clean, False if malware detected
        """
        # This is a placeholder - implement actual malware scanning
        # You could integrate with services like VirusTotal API
        return True
