"""
PostgreSQL Database Module - Production Ready
Zero-downtime migration: Supports PostgreSQL (Railway) with SQLite fallback
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

# Try PostgreSQL first
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
    logger.info("✓ psycopg2 available")
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("psycopg2 not available - PostgreSQL disabled")

# Always have SQLite as fallback
import sqlite3


class IMEIDatabase:
    """
    Universal database interface: PostgreSQL (Railway) or SQLite (local)

    Priority:
    1. DATABASE_URL (Railway PostgreSQL)
    2. SUPABASE_URL (Supabase PostgreSQL)
    3. SQLite (local fallback)
    """

    def __init__(self, db_path: str = 'imei_orders.db'):
        self.db_path = db_path
        self.conn = None
        self.use_postgres = False
        self.postgres_type = None  # 'railway' or 'supabase'

        logger.info("=== DATABASE INITIALIZATION ===")

        # Try Railway PostgreSQL first (DATABASE_URL or DATABASE_PUBLIC_URL)
        database_url = os.getenv('DATABASE_URL') or os.getenv('DATABASE_PUBLIC_URL')
        if database_url and POSTGRES_AVAILABLE:
            logger.info(f"Database connection URL found - attempting Railway PostgreSQL connection")
            if self._connect_postgres(database_url, 'railway'):
                return

        # Try Supabase PostgreSQL second (if we want to keep it)
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        if supabase_url and supabase_key and POSTGRES_AVAILABLE:
            logger.info("SUPABASE_URL found - attempting Supabase PostgreSQL connection")
            # Convert Supabase URL to PostgreSQL connection string
            postgres_url = self._supabase_to_postgres_url(supabase_url, supabase_key)
            if postgres_url and self._connect_postgres(postgres_url, 'supabase'):
                return

        # Fallback to SQLite
        logger.warning("No PostgreSQL available - using SQLite fallback")
        self._connect_sqlite()

    def _supabase_to_postgres_url(self, supabase_url: str, supabase_key: str) -> Optional[str]:
        """Convert Supabase URL to direct PostgreSQL connection string"""
        try:
            # Supabase direct DB connection (requires additional config)
            # For now, we'll skip Supabase and just use Railway
            return None
        except Exception as e:
            logger.error(f"Failed to parse Supabase URL: {e}")
            return None

    def _connect_postgres(self, database_url: str, db_type: str) -> bool:
        """Connect to PostgreSQL (Railway or Supabase)"""
        try:
            logger.info(f"Connecting to {db_type} PostgreSQL...")

            # Parse DATABASE_URL and connect
            self.conn = psycopg2.connect(database_url)
            self.use_postgres = True
            self.postgres_type = db_type

            logger.info(f"✓ Connected to {db_type} PostgreSQL")

            # Create tables if they don't exist
            self._create_tables_postgres()
            logger.info("✓ PostgreSQL tables verified/created")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to {db_type} PostgreSQL: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def _connect_sqlite(self):
        """Connect to SQLite (fallback)"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.use_postgres = False
            logger.info(f"✓ Connected to SQLite: {self.db_path}")
            self._create_tables_sqlite()
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise

    def _create_tables_postgres(self):
        """Create PostgreSQL tables"""
        cursor = self.conn.cursor()

        # Main orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(100) UNIQUE NOT NULL,
                service_name VARCHAR(255),
                service_id VARCHAR(100),
                imei VARCHAR(15) NOT NULL,
                imei2 VARCHAR(15),
                credits NUMERIC(10, 2),
                status VARCHAR(50),
                carrier VARCHAR(255),
                simlock VARCHAR(100),
                model VARCHAR(255),
                fmi VARCHAR(50),
                order_date TIMESTAMP,
                result_code TEXT,
                result_code_display TEXT,
                notes TEXT,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                serial_number VARCHAR(100),
                meid VARCHAR(100),
                gsma_status VARCHAR(100),
                purchase_date VARCHAR(50),
                applecare VARCHAR(50),
                tether_policy TEXT
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_imei ON orders(imei)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")

        self.conn.commit()

    def _create_tables_sqlite(self):
        """Create SQLite tables"""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                service_name TEXT,
                service_id TEXT,
                imei TEXT NOT NULL,
                imei2 TEXT,
                credits REAL,
                status TEXT,
                carrier TEXT,
                simlock TEXT,
                model TEXT,
                fmi TEXT,
                order_date TIMESTAMP,
                result_code TEXT,
                result_code_display TEXT,
                notes TEXT,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                serial_number TEXT,
                meid TEXT,
                gsma_status TEXT,
                purchase_date TEXT,
                applecare TEXT,
                tether_policy TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_imei ON orders(imei)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")

        self.conn.commit()

    def insert_order(self, order_data: Dict) -> Optional[int]:
        """Insert order (works with both PostgreSQL and SQLite)"""
        if self.use_postgres:
            return self._insert_order_postgres(order_data)
        else:
            return self._insert_order_sqlite(order_data)

    def _insert_order_postgres(self, order_data: Dict) -> Optional[int]:
        """Insert order into PostgreSQL"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO orders (
                    order_id, service_name, service_id, imei, imei2, credits,
                    status, carrier, simlock, model, fmi, order_date,
                    result_code, result_code_display, notes, raw_response
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (order_id) DO NOTHING
                RETURNING id
            """, (
                order_data.get('order_id'),
                order_data.get('service_name'),
                order_data.get('service_id'),
                order_data.get('imei'),
                order_data.get('imei2'),
                order_data.get('credits'),
                order_data.get('status', 'Pending'),
                order_data.get('carrier'),
                order_data.get('simlock'),
                order_data.get('model'),
                order_data.get('fmi'),
                order_data.get('order_date'),
                order_data.get('result_code'),
                order_data.get('result_code_display'),
                order_data.get('notes'),
                json.dumps(order_data.get('raw_response')) if order_data.get('raw_response') else None
            ))

            result = cursor.fetchone()
            self.conn.commit()

            return result[0] if result else None

        except Exception as e:
            logger.error(f"Failed to insert order to PostgreSQL: {e}")
            self.conn.rollback()
            return None

    def _insert_order_sqlite(self, order_data: Dict) -> Optional[int]:
        """Insert order into SQLite"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO orders (
                    order_id, service_name, service_id, imei, imei2, credits,
                    status, carrier, simlock, model, fmi, order_date,
                    result_code, result_code_display, notes, raw_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_data.get('order_id'),
                order_data.get('service_name'),
                order_data.get('service_id'),
                order_data.get('imei'),
                order_data.get('imei2'),
                order_data.get('credits'),
                order_data.get('status', 'Pending'),
                order_data.get('carrier'),
                order_data.get('simlock'),
                order_data.get('model'),
                order_data.get('fmi'),
                order_data.get('order_date'),
                order_data.get('result_code'),
                order_data.get('result_code_display'),
                order_data.get('notes'),
                json.dumps(order_data.get('raw_response')) if order_data.get('raw_response') else None
            ))

            self.conn.commit()
            return cursor.lastrowid if cursor.rowcount > 0 else None

        except Exception as e:
            logger.error(f"Failed to insert order to SQLite: {e}")
            return None

    def get_recent_orders(self, limit: int = 100) -> List[Dict]:
        """Get recent orders"""
        try:
            cursor = self.conn.cursor()

            if self.use_postgres:
                cursor.execute("""
                    SELECT * FROM orders
                    ORDER BY order_date DESC NULLS LAST, created_at DESC
                    LIMIT %s
                """, (limit,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                cursor.execute("""
                    SELECT * FROM orders
                    ORDER BY order_date DESC, created_at DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get recent orders: {e}")
            return []

    def get_orders_by_imei(self, imei: str) -> List[Dict]:
        """Get orders by IMEI"""
        try:
            cursor = self.conn.cursor()

            if self.use_postgres:
                cursor.execute("SELECT * FROM orders WHERE imei = %s ORDER BY order_date DESC", (imei,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                cursor.execute("SELECT * FROM orders WHERE imei = ? ORDER BY order_date DESC", (imei,))
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get orders by IMEI: {e}")
            return []

    def update_order_status(self, order_id: str, status: str, result_code: str = None,
                           result_code_display: str = None, result_data: Dict = None):
        """Update order with results"""
        try:
            cursor = self.conn.cursor()

            # Build update query
            update_fields = ['status = %s' if self.use_postgres else 'status = ?']
            params = [status]

            if result_code:
                update_fields.append('result_code = %s' if self.use_postgres else 'result_code = ?')
                params.append(result_code)

            if result_code_display:
                update_fields.append('result_code_display = %s' if self.use_postgres else 'result_code_display = ?')
                params.append(result_code_display)

            if result_data:
                for field in ['carrier', 'model', 'simlock', 'fmi', 'imei2', 'serial_number',
                             'meid', 'gsma_status', 'purchase_date', 'applecare', 'tether_policy']:
                    if result_data.get(field):
                        update_fields.append(f'{field} = %s' if self.use_postgres else f'{field} = ?')
                        params.append(result_data[field])

            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(order_id)

            query = f"UPDATE orders SET {', '.join(update_fields)} WHERE order_id = {'%s' if self.use_postgres else '?'}"
            cursor.execute(query, params)
            self.conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            self.conn.rollback()
            return False

    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Get orders by status"""
        try:
            cursor = self.conn.cursor()

            if self.use_postgres:
                cursor.execute("SELECT * FROM orders WHERE status = %s ORDER BY order_date DESC", (status,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY order_date DESC", (status,))
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get orders by status: {e}")
            return []

    def search_orders_by_imei(self, imei: str) -> List[Dict]:
        """Alias for get_orders_by_imei"""
        return self.get_orders_by_imei(imei)

    def get_order_count(self) -> int:
        """Get total order count"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get order count: {e}")
            return 0

    def record_batch_import(self, filename: str, rows_imported: int, rows_skipped: int, file_url: str = None):
        """Record batch import (optional feature)"""
        logger.info(f"Batch import: {filename} - {rows_imported} imported, {rows_skipped} skipped")
        # Could add import_history table later if needed

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Singleton pattern
_db_instance = None

def get_database(db_path: str = 'imei_orders.db') -> IMEIDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = IMEIDatabase(db_path)
    return _db_instance
