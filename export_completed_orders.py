#!/usr/bin/env python3
"""
Export Completed Orders to CSV and Upload to Supabase Storage

This module exports all completed IMEI orders to CSV format
and uploads them to Supabase Storage for cloud persistence.

Usage:
    python3 export_completed_orders.py

Or import and use programmatically:
    from export_completed_orders import export_completed_orders_to_csv
    csv_url = export_completed_orders_to_csv()
"""

import csv
import io
import logging
from datetime import datetime
from typing import Optional, List, Dict
from database import get_database
from supabase_storage import get_storage

logger = logging.getLogger(__name__)


def export_completed_orders_to_csv(status_filter: str = 'Completed') -> Optional[str]:
    """
    Export orders with specified status to CSV and upload to Supabase Storage.

    Args:
        status_filter: Order status to export (default: 'Completed')

    Returns:
        Public URL of uploaded CSV file, or None if failed

    Example:
        csv_url = export_completed_orders_to_csv()
        if csv_url:
            print(f"Exported to: {csv_url}")
    """
    try:
        # Get database connection
        db = get_database()
        logger.info(f"Fetching orders with status: {status_filter}")

        # Get all completed orders
        orders = db.get_orders_by_status(status_filter)

        if not orders:
            logger.warning(f"No orders found with status '{status_filter}'")
            return None

        logger.info(f"Found {len(orders)} {status_filter} orders to export")

        # Generate CSV in memory
        csv_buffer = io.StringIO()

        # Define CSV columns
        fieldnames = [
            'order_id',
            'imei',
            'imei2',
            'service_name',
            'service_id',
            'status',
            'carrier',
            'model',
            'simlock',
            'fmi',
            'credits',
            'order_date',
            'result_code',
            'result_code_display',
            'notes',
            'created_at',
            'updated_at'
        ]

        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()

        # Write order data
        for order in orders:
            # Convert order dict to CSV row
            row = {field: order.get(field, '') for field in fieldnames}
            writer.writerow(row)

        # Get CSV bytes
        csv_content = csv_buffer.getvalue()
        csv_bytes = csv_content.encode('utf-8')

        logger.info(f"Generated CSV with {len(orders)} rows ({len(csv_bytes)} bytes)")

        # Upload to Supabase Storage
        storage = get_storage()

        if not storage.available:
            logger.error("Supabase Storage not available - cannot upload CSV")
            return None

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"completed_orders_{timestamp}.csv"

        # Upload file
        file_url = storage.upload_file(filename, csv_bytes, content_type='text/csv')

        if file_url:
            logger.info(f"✅ Exported {len(orders)} completed orders to: {file_url}")
            return file_url
        else:
            logger.error("Failed to upload CSV to Supabase Storage")
            return None

    except Exception as e:
        logger.error(f"Failed to export completed orders: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def export_all_orders_to_csv(limit: int = 10000) -> Optional[str]:
    """
    Export all recent orders (any status) to CSV and upload to Supabase Storage.

    Args:
        limit: Maximum number of orders to export (default: 10000)

    Returns:
        Public URL of uploaded CSV file, or None if failed
    """
    try:
        # Get database connection
        db = get_database()
        logger.info(f"Fetching recent {limit} orders")

        # Get recent orders
        orders = db.get_recent_orders(limit=limit)

        if not orders:
            logger.warning("No orders found to export")
            return None

        logger.info(f"Found {len(orders)} orders to export")

        # Generate CSV in memory
        csv_buffer = io.StringIO()

        # Define CSV columns
        fieldnames = [
            'order_id',
            'imei',
            'imei2',
            'service_name',
            'service_id',
            'status',
            'carrier',
            'model',
            'simlock',
            'fmi',
            'credits',
            'order_date',
            'result_code',
            'result_code_display',
            'notes',
            'created_at',
            'updated_at'
        ]

        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()

        # Write order data
        for order in orders:
            # Convert order dict to CSV row
            row = {field: order.get(field, '') for field in fieldnames}
            writer.writerow(row)

        # Get CSV bytes
        csv_content = csv_buffer.getvalue()
        csv_bytes = csv_content.encode('utf-8')

        logger.info(f"Generated CSV with {len(orders)} rows ({len(csv_bytes)} bytes)")

        # Upload to Supabase Storage
        storage = get_storage()

        if not storage.available:
            logger.error("Supabase Storage not available - cannot upload CSV")
            return None

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"all_orders_{timestamp}.csv"

        # Upload file
        file_url = storage.upload_file(filename, csv_bytes, content_type='text/csv')

        if file_url:
            logger.info(f"✅ Exported {len(orders)} orders to: {file_url}")
            return file_url
        else:
            logger.error("Failed to upload CSV to Supabase Storage")
            return None

    except Exception as e:
        logger.error(f"Failed to export all orders: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def list_exported_csvs(limit: int = 20) -> List[Dict]:
    """
    List all exported CSV files in Supabase Storage.

    Args:
        limit: Maximum number of files to return

    Returns:
        List of file metadata dictionaries
    """
    try:
        storage = get_storage()

        if not storage.available:
            logger.warning("Supabase Storage not available")
            return []

        files = storage.list_files(limit=limit)
        logger.info(f"Found {len(files)} exported CSV files")
        return files

    except Exception as e:
        logger.error(f"Failed to list exported CSVs: {e}")
        return []


if __name__ == '__main__':
    """
    Command-line usage: Export completed orders to CSV
    """
    import sys

    # Set up logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Export Completed Orders to CSV")
    print("=" * 60)
    print()

    # Check command-line arguments
    status_filter = 'Completed'
    if len(sys.argv) > 1:
        status_filter = sys.argv[1]
        print(f"Exporting orders with status: {status_filter}")
    else:
        print(f"Exporting orders with status: {status_filter} (default)")
        print(f"Usage: python3 {sys.argv[0]} [status]")
        print(f"Example: python3 {sys.argv[0]} 'In Process'")

    print()

    # Export completed orders
    csv_url = export_completed_orders_to_csv(status_filter)

    print()
    print("=" * 60)
    if csv_url:
        print("✅ Export successful!")
        print(f"CSV URL: {csv_url}")
        print()
        print("You can:")
        print(f"1. Download: curl -o export.csv '{csv_url}'")
        print(f"2. Share the URL with your team")
        print(f"3. Import to Excel, Google Sheets, etc.")
    else:
        print("❌ Export failed")
        print("Check:")
        print("1. SUPABASE_URL and SUPABASE_KEY are set in .env")
        print("2. Supabase Storage bucket 'batch-uploads' exists")
        print("3. Database has orders with the specified status")
    print("=" * 60)
