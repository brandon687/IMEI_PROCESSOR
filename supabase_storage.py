"""
Supabase Storage Module for CSV/Excel File Storage

This module handles uploading batch CSV/Excel files to Supabase Storage
so they are persisted in the cloud, not lost on Railway restarts.

Features:
- Upload CSV/Excel files to Supabase Storage
- Download files for processing
- List all uploaded files
- Delete old files
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not available")


class SupabaseFileStorage:
    """
    Manages file uploads to Supabase Storage.

    Usage:
        storage = SupabaseFileStorage()
        file_url = storage.upload_file('batch_orders.csv', file_data)
        files = storage.list_files()
    """

    def __init__(self, bucket_name: str = 'batch-uploads'):
        """
        Initialize Supabase Storage client.

        Args:
            bucket_name: Name of storage bucket (default: 'batch-uploads')
        """
        self.bucket_name = bucket_name
        self.client: Optional[Client] = None
        self.available = False

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not set - file storage disabled")
            return

        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase library not installed - file storage disabled")
            return

        try:
            self.client = create_client(supabase_url, supabase_key)
            self.available = True
            logger.info(f"✅ Supabase Storage initialized: bucket '{bucket_name}'")

            # Ensure bucket exists
            self._ensure_bucket_exists()

        except Exception as e:
            logger.error(f"Failed to initialize Supabase Storage: {e}")
            self.available = False

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            # Try to list files (will fail if bucket doesn't exist)
            self.client.storage.from_(self.bucket_name).list()
            logger.info(f"✅ Bucket '{self.bucket_name}' exists")
        except Exception as e:
            error_msg = str(e).lower()
            if 'not found' in error_msg or 'does not exist' in error_msg:
                logger.info(f"Bucket '{self.bucket_name}' does not exist - needs manual creation")
                logger.info(f"Go to Supabase Dashboard → Storage → Create bucket: {self.bucket_name}")
            else:
                logger.warning(f"Could not verify bucket: {e}")

    def upload_file(self, filename: str, file_data: bytes,
                   content_type: str = 'text/csv') -> Optional[str]:
        """
        Upload file to Supabase Storage.

        Args:
            filename: Original filename (e.g., 'orders_2025-11-15.csv')
            file_data: File content as bytes
            content_type: MIME type (default: 'text/csv')

        Returns:
            Public URL of uploaded file, or None if failed
        """
        if not self.available:
            logger.warning("Supabase Storage not available - file not uploaded")
            return None

        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_ext = Path(filename).suffix
            unique_filename = f"{timestamp}_{filename}"

            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_data,
                file_options={
                    "content-type": content_type,
                    "upsert": "true"  # Overwrite if exists
                }
            )

            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_filename)

            logger.info(f"✅ Uploaded file: {unique_filename}")
            logger.info(f"   URL: {public_url}")

            return public_url

        except Exception as e:
            logger.error(f"Failed to upload file to Supabase Storage: {e}")
            return None

    def upload_file_path(self, file_path: str) -> Optional[str]:
        """
        Upload file from filesystem path.

        Args:
            file_path: Path to file on disk

        Returns:
            Public URL of uploaded file, or None if failed
        """
        if not self.available:
            return None

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            filename = os.path.basename(file_path)

            # Detect content type
            if file_path.endswith('.csv'):
                content_type = 'text/csv'
            elif file_path.endswith(('.xlsx', '.xls')):
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                content_type = 'application/octet-stream'

            return self.upload_file(filename, file_data, content_type)

        except Exception as e:
            logger.error(f"Failed to upload file from path: {e}")
            return None

    def list_files(self, limit: int = 100) -> List[Dict]:
        """
        List all uploaded files in bucket.

        Args:
            limit: Maximum number of files to return

        Returns:
            List of file metadata dictionaries
        """
        if not self.available:
            return []

        try:
            files = self.client.storage.from_(self.bucket_name).list()

            # Sort by created date (newest first)
            files_sorted = sorted(
                files,
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )

            return files_sorted[:limit]

        except Exception as e:
            logger.error(f"Failed to list files from Supabase Storage: {e}")
            return []

    def download_file(self, filename: str) -> Optional[bytes]:
        """
        Download file from Supabase Storage.

        Args:
            filename: Name of file in storage

        Returns:
            File content as bytes, or None if failed
        """
        if not self.available:
            return None

        try:
            response = self.client.storage.from_(self.bucket_name).download(filename)
            logger.info(f"✅ Downloaded file: {filename}")
            return response

        except Exception as e:
            logger.error(f"Failed to download file from Supabase Storage: {e}")
            return None

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from Supabase Storage.

        Args:
            filename: Name of file in storage

        Returns:
            True if deleted, False if failed
        """
        if not self.available:
            return False

        try:
            self.client.storage.from_(self.bucket_name).remove([filename])
            logger.info(f"✅ Deleted file: {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file from Supabase Storage: {e}")
            return False

    def get_file_url(self, filename: str) -> Optional[str]:
        """
        Get public URL for a file.

        Args:
            filename: Name of file in storage

        Returns:
            Public URL or None if not available
        """
        if not self.available:
            return None

        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(filename)
        except Exception as e:
            logger.error(f"Failed to get file URL: {e}")
            return None

    def delete_old_files(self, days: int = 30) -> int:
        """
        Delete files older than specified days.

        Args:
            days: Delete files older than this many days

        Returns:
            Number of files deleted
        """
        if not self.available:
            return 0

        try:
            from datetime import timedelta

            files = self.list_files(limit=1000)
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0

            for file in files:
                created_at = file.get('created_at')
                if created_at:
                    file_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if file_date < cutoff_date:
                        if self.delete_file(file['name']):
                            deleted_count += 1

            logger.info(f"✅ Deleted {deleted_count} old files (older than {days} days)")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete old files: {e}")
            return 0


# Singleton instance
_storage_instance = None

def get_storage() -> SupabaseFileStorage:
    """Get singleton storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = SupabaseFileStorage()
    return _storage_instance
