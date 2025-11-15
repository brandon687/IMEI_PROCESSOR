"""
Database module with dual support: SQLite (local) + Supabase (production)

Automatically detects environment and uses appropriate database:
- SUPABASE_URL set → Use Supabase (PostgreSQL)
- SUPABASE_URL not set → Use SQLite (local file)

This allows seamless local development with SQLite and production with Supabase.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

# Try to import Supabase (will fail if not installed)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not available - will use SQLite only")

# Always import sqlite3 for local fallback
import sqlite3


class IMEIDatabase:
    """
    Unified database interface supporting both SQLite and Supabase.

    Usage:
        db = IMEIDatabase()  # Auto-detects from environment
        db.insert_order({...})
        orders = db.get_recent_orders(100)

    Environment Variables:
        SUPABASE_URL - If set, use Supabase
        SUPABASE_KEY - Required if SUPABASE_URL is set

    Falls back to SQLite (imei_orders.db) if Supabase not configured.
    """

    def __init__(self, db_path: str = 'imei_orders.db'):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database (used if Supabase not configured)
        """
        self.db_path = db_path
        self.conn = None
        self.supabase_client: Optional[Client] = None
        self.use_supabase = False

        # Detect which database to use
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if supabase_url and supabase_key and SUPABASE_AVAILABLE:
            self._connect_supabase(supabase_url, supabase_key)
        else:
            if supabase_url:
                logger.warning("SUPABASE_URL set but Supabase not available or SUPABASE_KEY missing - falling back to SQLite")
            self._connect_sqlite()

    def _connect_supabase(self, url: str, key: str):
        """Connect to Supabase (PostgreSQL)"""
        try:
            self.supabase_client = create_client(url, key)
            self.use_supabase = True
            logger.info(f"✓ Connected to Supabase: {url}")

            # Verify connection by pinging
            self.supabase_client.table('orders').select('id').limit(1).execute()
            logger.info("✓ Supabase connection verified")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            logger.warning("Falling back to SQLite")
            self._connect_sqlite()

    def _connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.use_supabase = False
            logger.info(f"✓ Connected to SQLite: {self.db_path}")
            self._create_tables_sqlite()
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise

    def _create_tables_sqlite(self):
        """Create SQLite tables if they don't exist"""
        cursor = self.conn.cursor()

        # Main orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_imei ON orders(imei)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id ON orders(order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON orders(status)')

        # Import history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                rows_imported INTEGER,
                rows_skipped INTEGER,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()
        logger.info("✓ SQLite tables created/verified")

    def insert_order(self, order_data: Dict) -> Optional[int]:
        """
        Insert new order into database.

        Args:
            order_data: Dictionary with order fields

        Returns:
            Order ID if successful, None if duplicate
        """
        if self.use_supabase:
            return self._insert_order_supabase(order_data)
        else:
            return self._insert_order_sqlite(order_data)

    def _insert_order_sqlite(self, order_data: Dict) -> Optional[int]:
        """Insert order into SQLite"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    order_id, service_name, service_id, imei, imei2,
                    credits, status, carrier, simlock, model, fmi,
                    order_date, result_code, result_code_display, notes, raw_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
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
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate order: {order_data.get('order_id')}")
            return None
        except Exception as e:
            logger.error(f"Failed to insert order: {e}")
            return None

    def _insert_order_supabase(self, order_data: Dict) -> Optional[int]:
        """Insert order into Supabase"""
        try:
            # Prepare data for Supabase
            data = {
                'order_id': order_data.get('order_id'),
                'service_name': order_data.get('service_name'),
                'service_id': order_data.get('service_id'),
                'imei': order_data.get('imei'),
                'imei2': order_data.get('imei2'),
                'credits': order_data.get('credits'),
                'status': order_data.get('status', 'Pending'),
                'carrier': order_data.get('carrier'),
                'simlock': order_data.get('simlock'),
                'model': order_data.get('model'),
                'fmi': order_data.get('fmi'),
                'order_date': order_data.get('order_date'),
                'result_code': order_data.get('result_code'),
                'result_code_display': order_data.get('result_code_display'),
                'notes': order_data.get('notes'),
                'raw_response': json.dumps(order_data.get('raw_response')) if order_data.get('raw_response') else None
            }

            response = self.supabase_client.table('orders').insert(data).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            return None

        except Exception as e:
            error_msg = str(e)
            if 'duplicate key value' in error_msg.lower():
                logger.warning(f"Duplicate order: {order_data.get('order_id')}")
                return None
            else:
                logger.error(f"Failed to insert order to Supabase: {e}")
                return None

    def get_recent_orders(self, limit: int = 100) -> List[Dict]:
        """Get recent orders, sorted by order_date descending"""
        if self.use_supabase:
            return self._get_recent_orders_supabase(limit)
        else:
            return self._get_recent_orders_sqlite(limit)

    def _get_recent_orders_sqlite(self, limit: int) -> List[Dict]:
        """Get recent orders from SQLite"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            ORDER BY order_date DESC, created_at DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def _get_recent_orders_supabase(self, limit: int) -> List[Dict]:
        """Get recent orders from Supabase"""
        try:
            response = self.supabase_client.table('orders') \
                .select('*') \
                .order('order_date', desc=True) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to fetch recent orders from Supabase: {e}")
            return []

    def get_orders_by_imei(self, imei: str) -> List[Dict]:
        """Get all orders for a specific IMEI"""
        if self.use_supabase:
            return self._get_orders_by_imei_supabase(imei)
        else:
            return self._get_orders_by_imei_sqlite(imei)

    def _get_orders_by_imei_sqlite(self, imei: str) -> List[Dict]:
        """Get orders by IMEI from SQLite"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            WHERE imei = ?
            ORDER BY order_date DESC
        ''', (imei,))
        return [dict(row) for row in cursor.fetchall()]

    def _get_orders_by_imei_supabase(self, imei: str) -> List[Dict]:
        """Get orders by IMEI from Supabase"""
        try:
            response = self.supabase_client.table('orders') \
                .select('*') \
                .eq('imei', imei) \
                .order('order_date', desc=True) \
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to fetch orders by IMEI from Supabase: {e}")
            return []

    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Get all orders with a specific status"""
        if self.use_supabase:
            return self._get_orders_by_status_supabase(status)
        else:
            return self._get_orders_by_status_sqlite(status)

    def _get_orders_by_status_sqlite(self, status: str) -> List[Dict]:
        """Get orders by status from SQLite"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            WHERE status = ?
            ORDER BY order_date DESC
        ''', (status,))
        return [dict(row) for row in cursor.fetchall()]

    def _get_orders_by_status_supabase(self, status: str) -> List[Dict]:
        """Get orders by status from Supabase"""
        try:
            response = self.supabase_client.table('orders') \
                .select('*') \
                .eq('status', status) \
                .order('order_date', desc=True) \
                .execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to fetch orders by status from Supabase: {e}")
            return []

    def update_order_status(self, order_id: str, status: str, result_code: str = None,
                           result_code_display: str = None, result_data: Dict = None):
        """Update order with results from API"""
        if self.use_supabase:
            return self._update_order_status_supabase(order_id, status, result_code,
                                                     result_code_display, result_data)
        else:
            return self._update_order_status_sqlite(order_id, status, result_code,
                                                   result_code_display, result_data)

    def _update_order_status_sqlite(self, order_id: str, status: str, result_code: str = None,
                                    result_code_display: str = None, result_data: Dict = None):
        """Update order status in SQLite"""
        try:
            cursor = self.conn.cursor()

            update_fields = ['status = ?']
            params = [status]

            if result_code:
                update_fields.append('result_code = ?')
                params.append(result_code)

            if result_code_display:
                update_fields.append('result_code_display = ?')
                params.append(result_code_display)

            if result_data:
                if result_data.get('carrier'):
                    update_fields.append('carrier = ?')
                    params.append(result_data['carrier'])
                if result_data.get('model'):
                    update_fields.append('model = ?')
                    params.append(result_data['model'])
                if result_data.get('simlock'):
                    update_fields.append('simlock = ?')
                    params.append(result_data['simlock'])
                if result_data.get('fmi'):
                    update_fields.append('fmi = ?')
                    params.append(result_data['fmi'])

            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(order_id)

            query = f"UPDATE orders SET {', '.join(update_fields)} WHERE order_id = ?"
            cursor.execute(query, params)
            self.conn.commit()

            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update order status in SQLite: {e}")
            return False

    def _update_order_status_supabase(self, order_id: str, status: str, result_code: str = None,
                                     result_code_display: str = None, result_data: Dict = None):
        """Update order status in Supabase"""
        try:
            update_data = {'status': status}

            if result_code:
                update_data['result_code'] = result_code
            if result_code_display:
                update_data['result_code_display'] = result_code_display

            if result_data:
                if result_data.get('carrier'):
                    update_data['carrier'] = result_data['carrier']
                if result_data.get('model'):
                    update_data['model'] = result_data['model']
                if result_data.get('simlock'):
                    update_data['simlock'] = result_data['simlock']
                if result_data.get('fmi'):
                    update_data['fmi'] = result_data['fmi']

            response = self.supabase_client.table('orders') \
                .update(update_data) \
                .eq('order_id', order_id) \
                .execute()

            return True
        except Exception as e:
            logger.error(f"Failed to update order status in Supabase: {e}")
            return False

    def get_order_count(self) -> int:
        """Get total number of orders"""
        if self.use_supabase:
            return self._get_order_count_supabase()
        else:
            return self._get_order_count_sqlite()

    def _get_order_count_sqlite(self) -> int:
        """Get order count from SQLite"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM orders')
        return cursor.fetchone()[0]

    def _get_order_count_supabase(self) -> int:
        """Get order count from Supabase"""
        try:
            response = self.supabase_client.table('orders') \
                .select('id', count='exact') \
                .execute()
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Failed to get order count from Supabase: {e}")
            return 0

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")
        # Supabase client doesn't need explicit closing


# Singleton instance
_db_instance = None

def get_database(db_path: str = 'imei_orders.db') -> IMEIDatabase:
    """
    Get singleton database instance.

    Automatically uses Supabase if SUPABASE_URL is set, otherwise SQLite.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = IMEIDatabase(db_path)
    return _db_instance


# For backwards compatibility
def get_db_safe() -> Optional[IMEIDatabase]:
    """
    Get database instance with error handling (never crashes).
    Returns None if database unavailable.
    """
    try:
        return get_database()
    except Exception as e:
        logger.error(f"Failed to get database: {e}")
        return None
