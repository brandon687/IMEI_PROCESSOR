"""
Database module for storing IMEI order data locally
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class IMEIDatabase:
    """SQLite database for storing IMEI order data"""

    def __init__(self, db_path: str = 'imei_orders.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
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

        # Add result_code_display column if it doesn't exist (migration)
        try:
            cursor.execute('ALTER TABLE orders ADD COLUMN result_code_display TEXT')
            logger.info("Added result_code_display column to orders table")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' not in str(e).lower():
                logger.warning(f"Could not add result_code_display column: {e}")

        # Index for fast lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_imei ON orders(imei)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_order_id ON orders(order_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status ON orders(status)
        ''')

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
        logger.info("Database tables created successfully")

    def insert_order(self, order_data: Dict) -> Optional[int]:
        """
        Insert a new order into the database

        Args:
            order_data: Dictionary containing order information

        Returns:
            Row ID of inserted order or None if failed
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO orders (
                    order_id, service_name, service_id, imei, imei2,
                    credits, status, carrier, simlock, model, fmi,
                    order_date, result_code, notes, raw_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_data.get('order_id'),
                order_data.get('service_name'),
                order_data.get('service_id'),
                order_data.get('imei'),
                order_data.get('imei2'),
                order_data.get('credits'),
                order_data.get('status'),
                order_data.get('carrier'),
                order_data.get('simlock'),
                order_data.get('model'),
                order_data.get('fmi'),
                order_data.get('order_date'),
                order_data.get('result_code'),
                order_data.get('notes'),
                order_data.get('raw_response')
            ))

            self.conn.commit()
            logger.info(f"Inserted order {order_data.get('order_id')} for IMEI {order_data.get('imei')}")
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            logger.warning(f"Order {order_data.get('order_id')} already exists in database")
            return None
        except Exception as e:
            logger.error(f"Failed to insert order: {e}")
            self.conn.rollback()
            return None

    def update_order_status(self, order_id: str, status: str, code: str = None, code_display: str = None, service_name: str = None, result_data: Dict = None):
        """Update order status and results

        Args:
            order_id: Order ID to update
            status: New status
            code: Original CODE from API (with HTML tags) - for record keeping
            code_display: Cleaned CODE for display (without HTML tags)
            service_name: Service/package name from API
            result_data: Dictionary with parsed fields (carrier, model, etc.)
        """
        cursor = self.conn.cursor()

        try:
            if result_data:
                cursor.execute('''
                    UPDATE orders
                    SET status = ?,
                        service_name = ?,
                        carrier = ?,
                        simlock = ?,
                        model = ?,
                        fmi = ?,
                        imei2 = ?,
                        result_code = ?,
                        result_code_display = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                ''', (
                    status,
                    service_name or result_data.get('service_name'),
                    result_data.get('carrier'),
                    result_data.get('simlock'),
                    result_data.get('model'),
                    result_data.get('fmi'),
                    result_data.get('imei2'),
                    result_data.get('result_code') or code,
                    result_data.get('result_code_display') or code_display,
                    order_id
                ))
            else:
                # Simple status update (from API sync)
                if code:
                    cursor.execute('''
                        UPDATE orders
                        SET status = ?,
                            result_code = ?,
                            result_code_display = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE order_id = ?
                    ''', (status, code, code_display or code, order_id))
                else:
                    cursor.execute('''
                        UPDATE orders
                        SET status = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE order_id = ?
                    ''', (status, order_id))

            self.conn.commit()
            logger.info(f"Updated order {order_id} status to {status}")

        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            self.conn.rollback()

    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order by order ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_orders_by_imei(self, imei: str) -> List[Dict]:
        """Get all orders for a specific IMEI"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            WHERE imei = ?
            ORDER BY order_date DESC
        ''', (imei,))

        return [dict(row) for row in cursor.fetchall()]

    def search_orders_by_imei(self, imei: str) -> List[Dict]:
        """Alias for get_orders_by_imei() for backward compatibility"""
        return self.get_orders_by_imei(imei)

    def get_recent_orders(self, limit: int = 50) -> List[Dict]:
        """Get recent orders"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            ORDER BY order_date DESC
            LIMIT ?
        ''', (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Get orders by status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            WHERE status = ?
            ORDER BY order_date DESC
        ''', (status,))

        return [dict(row) for row in cursor.fetchall()]

    def search_orders_by_status(self, statuses: List[str]) -> List[Dict]:
        """Get orders by multiple status values"""
        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(statuses))
        cursor.execute(f'''
            SELECT * FROM orders
            WHERE status IN ({placeholders})
            ORDER BY order_date DESC
        ''', statuses)

        return [dict(row) for row in cursor.fetchall()]

    def get_orders_by_imeis(self, imeis: List[str]) -> List[Dict]:
        """Get all orders for multiple IMEIs (batch search)"""
        if not imeis:
            return []

        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(imeis))
        cursor.execute(f'''
            SELECT * FROM orders
            WHERE imei IN ({placeholders})
            ORDER BY order_date DESC
        ''', imeis)

        return [dict(row) for row in cursor.fetchall()]

    def search_orders(self, query: str) -> List[Dict]:
        """Search orders by IMEI, model, carrier, etc."""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"

        cursor.execute('''
            SELECT * FROM orders
            WHERE imei LIKE ?
               OR model LIKE ?
               OR carrier LIKE ?
               OR order_id LIKE ?
            ORDER BY order_date DESC
            LIMIT 100
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Total orders
        cursor.execute('SELECT COUNT(*) FROM orders')
        stats['total_orders'] = cursor.fetchone()[0]

        # Orders by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM orders
            GROUP BY status
        ''')
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

        # Total credits spent
        cursor.execute('SELECT SUM(credits) FROM orders WHERE credits IS NOT NULL')
        result = cursor.fetchone()[0]
        stats['total_credits'] = float(result) if result else 0.0

        # Orders today
        cursor.execute('''
            SELECT COUNT(*) FROM orders
            WHERE DATE(order_date) = DATE('now')
        ''')
        stats['orders_today'] = cursor.fetchone()[0]

        return stats

    def import_from_hammer_export(self, excel_data: List[Dict]) -> Dict:
        """
        Import orders from Hammer Fusion export data

        Args:
            excel_data: List of dictionaries from Excel export

        Returns:
            Dictionary with import statistics
        """
        imported = 0
        skipped = 0

        for row in excel_data:
            # Skip empty rows
            if not row.get('IMEI NO.'):
                continue

            # Parse the data
            order_data = {
                'order_id': None,  # Hammer exports don't include order ID
                'service_name': row.get('SERVICE'),
                'service_id': None,
                'imei': str(row.get('IMEI NO.')).strip() if row.get('IMEI NO.') else None,
                'imei2': row.get('IMEI 2'),
                'credits': self._parse_credits(row.get('CREDITS')),
                'status': row.get('STATUS'),
                'carrier': row.get('CARRIER'),
                'simlock': row.get('SIMLOCK'),
                'model': row.get('MODEL'),
                'fmi': row.get('FMI'),
                'order_date': self._parse_date(row.get('ORDER DATE')),
                'result_code': row.get('CODE'),
                'notes': row.get('NOTES'),
                'raw_response': json.dumps(row)
            }

            # Check if order already exists by IMEI (update instead of duplicate)
            existing_order = self.get_orders_by_imei(order_data['imei'])

            if existing_order:
                # Update existing order with Hammer Fusion data
                order_id = existing_order[0]['order_id']
                self.update_order_status(
                    order_id=order_id,
                    status=order_data['status'],
                    code=order_data['result_code'],
                    result_data={
                        'carrier': order_data['carrier'],
                        'simlock': order_data['simlock'],
                        'model': order_data['model'],
                        'fmi': order_data['fmi'],
                        'imei2': order_data['imei2'],
                        'result_code': order_data['result_code']
                    }
                )
                imported += 1
            else:
                # Generate pseudo order ID from IMEI + date if not present
                if order_data['imei'] and order_data['order_date']:
                    order_data['order_id'] = f"IMPORT_{order_data['imei']}_{order_data['order_date'].replace(' ', '_').replace(':', '-')}"

                if self.insert_order(order_data):
                    imported += 1
                else:
                    skipped += 1

        # Record import history
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO import_history (filename, rows_imported, rows_skipped)
            VALUES (?, ?, ?)
        ''', ('hammer_export', imported, skipped))
        self.conn.commit()

        return {
            'imported': imported,
            'skipped': skipped,
            'total': imported + skipped
        }

    def _parse_credits(self, value) -> Optional[float]:
        """Parse credits value from string like '$0.08'"""
        if not value:
            return None
        try:
            # Remove $ and convert to float
            return float(str(value).replace('$', '').strip())
        except:
            return None

    def _parse_date(self, value) -> Optional[str]:
        """Parse date value"""
        if not value:
            return None
        # Convert to string if it's a datetime object
        return str(value)

    def export_to_csv(self, output_path: str, filters: Dict = None):
        """Export orders to CSV file"""
        import csv

        cursor = self.conn.cursor()

        # Build query based on filters
        query = 'SELECT * FROM orders WHERE 1=1'
        params = []

        if filters:
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('start_date'):
                query += ' AND order_date >= ?'
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += ' AND order_date <= ?'
                params.append(filters['end_date'])

        query += ' ORDER BY order_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            return 0

        # Write to CSV
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                row_dict = dict(row)
                # Convert multi-line CODE to single-line format for CSV export
                if 'result_code_display' in row_dict and row_dict['result_code_display']:
                    row_dict['result_code_display'] = row_dict['result_code_display'].replace('\n', ' - ')
                writer.writerow(row_dict)

        return len(rows)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Global database instance
_db_instance = None


def get_database() -> IMEIDatabase:
    """Get or create global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = IMEIDatabase()
    return _db_instance
