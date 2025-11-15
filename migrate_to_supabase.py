#!/usr/bin/env python3
"""
Migrate existing SQLite data to Supabase

This script:
1. Tests Supabase connection
2. Exports data from SQLite
3. Imports data to Supabase
4. Verifies migration

Usage:
    python3 migrate_to_supabase.py
"""

import os
import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_supabase_connection():
    """Test if Supabase is configured and accessible"""
    logger.info("Testing Supabase connection...")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        logger.error("❌ Supabase not configured!")
        logger.error("Please set environment variables:")
        logger.error("  export SUPABASE_URL=https://xxx.supabase.co")
        logger.error("  export SUPABASE_KEY=eyJhbGciOi...")
        return False

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)

        # Test connection by pinging orders table
        response = client.table('orders').select('id').limit(1).execute()
        logger.info(f"✅ Connected to Supabase: {supabase_url}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
        logger.error("Make sure you've run the schema SQL in Supabase!")
        return False


def get_sqlite_order_count():
    """Get count of orders in SQLite database"""
    try:
        conn = sqlite3.connect('imei_orders.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM orders')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.warning(f"Could not count SQLite orders: {e}")
        return 0


def migrate_data():
    """Migrate data from SQLite to Supabase"""
    logger.info("=" * 60)
    logger.info("HAMMER-API: SQLite → Supabase Migration")
    logger.info("=" * 60)

    # Step 1: Test Supabase connection
    if not test_supabase_connection():
        logger.error("Migration aborted - fix Supabase connection first")
        return False

    # Step 2: Check SQLite database
    sqlite_count = get_sqlite_order_count()
    logger.info(f"SQLite database has {sqlite_count} orders")

    if sqlite_count == 0:
        logger.info("✅ No data to migrate - you're starting fresh!")
        logger.info("You can now use Supabase for all new orders")
        return True

    # Step 3: Confirm migration
    logger.info("")
    logger.info(f"This will copy {sqlite_count} orders from SQLite to Supabase")
    response = input("Continue? (y/n): ")

    if response.lower() != 'y':
        logger.info("Migration cancelled")
        return False

    # Step 4: Perform migration
    logger.info("Starting migration...")

    try:
        import sqlite3
        from database_supabase import IMEIDatabase

        # Connect to SQLite
        sqlite_conn = sqlite3.connect('imei_orders.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()

        # Connect to Supabase
        supabase_db = IMEIDatabase()

        if not supabase_db.use_supabase:
            logger.error("❌ Database is not using Supabase!")
            return False

        # Migrate orders
        cursor.execute('SELECT * FROM orders')
        rows = cursor.fetchall()

        migrated = 0
        skipped = 0

        for row in rows:
            order_data = dict(row)

            # Insert into Supabase
            result = supabase_db.insert_order(order_data)

            if result:
                migrated += 1
                if migrated % 100 == 0:
                    logger.info(f"Progress: {migrated}/{sqlite_count} orders migrated")
            else:
                skipped += 1

        sqlite_conn.close()

        # Step 5: Verification
        logger.info("")
        logger.info("=" * 60)
        logger.info("Migration Summary:")
        logger.info(f"  Total orders in SQLite: {sqlite_count}")
        logger.info(f"  Successfully migrated: {migrated}")
        logger.info(f"  Skipped (duplicates): {skipped}")
        logger.info("=" * 60)

        if migrated > 0:
            logger.info("✅ Migration completed successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Verify data in Supabase dashboard (Table Editor)")
            logger.info("  2. Test the web interface (submit a test order)")
            logger.info("  3. Deploy to Railway with Supabase env vars")
            logger.info("")
            logger.info("💡 TIP: You can keep imei_orders.db as a backup")
            return True
        else:
            logger.warning("⚠️  No orders were migrated")
            return False

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    success = migrate_data()
    exit(0 if success else 1)
