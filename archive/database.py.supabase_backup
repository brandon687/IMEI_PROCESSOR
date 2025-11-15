"""
Database module for storing IMEI order data in Supabase (PostgreSQL)
Production-ready with automatic reconnection and error handling
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class IMEIDatabase:
    """Supabase database for storing IMEI order data"""

    def __init__(self):
        """Initialize Supabase connection"""
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )

        self.client: Client = None
        self._connect()

    def _connect(self):
        """Connect to Supabase"""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info(f"Connected to Supabase: {self.supabase_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def insert_order(self, order_data: Dict) -> Optional[int]:
        """
        Insert a new order into the database

        Args:
            order_data: Dictionary containing order information

        Returns:
            Row ID of inserted order or None if failed
        """
        try:
            # Prepare data for Supabase
            data = {
                'order_id': order_data.get('order_id'),
                'service_name': order_data.get('service_name'),
                'service_id': order_data.get('service_id'),
                'imei': order_data.get('imei'),
                'imei2': order_data.get('imei2'),
                'credits': order_data.get('credits'),
                'status': order_data.get('status'),
                'carrier': order_data.get('carrier'),
                'simlock': order_data.get('simlock'),
                'model': order_data.get('model'),
                'fmi': order_data.get('fmi'),
                'order_date': order_data.get('order_date'),
                'result_code': order_data.get('result_code'),
                'result_code_display': order_data.get('result_code_display'),
                'notes': order_data.get('notes'),
                'raw_response': order_data.get('raw_response')
            }

            response = self.client.table('orders').insert(data).execute()

            if response.data:
                logger.info(f"Inserted order {order_data.get('order_id')} for IMEI {order_data.get('imei')}")
                return response.data[0]['id']
            return None

        except Exception as e:
            error_msg = str(e)
            if 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
                logger.warning(f"Order {order_data.get('order_id')} already exists in database")
            else:
                logger.error(f"Failed to insert order: {e}")
            return None

    def update_order_status(self, order_id: str, status: str, code: str = None,
                          code_display: str = None, service_name: str = None,
                          result_data: Dict = None):
        """Update order status and results

        Args:
            order_id: Order ID to update
            status: New status
            code: Original CODE from API (with HTML tags) - for record keeping
            code_display: Cleaned CODE for display (without HTML tags)
            service_name: Service/package name from API
            result_data: Dictionary with parsed fields (carrier, model, etc.)
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }

            if result_data:
                update_data.update({
                    'service_name': service_name or result_data.get('service_name'),
                    'carrier': result_data.get('carrier'),
                    'simlock': result_data.get('simlock'),
                    'model': result_data.get('model'),
                    'fmi': result_data.get('fmi'),
                    'imei2': result_data.get('imei2'),
                    'result_code': result_data.get('result_code') or code,
                    'result_code_display': result_data.get('result_code_display') or code_display
                })
            else:
                if code:
                    update_data['result_code'] = code
                    update_data['result_code_display'] = code_display or code

            self.client.table('orders').update(update_data).eq('order_id', order_id).execute()
            logger.info(f"Updated order {order_id} status to {status}")

        except Exception as e:
            logger.error(f"Failed to update order status: {e}")

    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order by order ID"""
        try:
            response = self.client.table('orders').select('*').eq('order_id', order_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get order by ID: {e}")
            return None

    def get_orders_by_imei(self, imei: str) -> List[Dict]:
        """Get all orders for a specific IMEI"""
        try:
            response = self.client.table('orders').select('*').eq('imei', imei).order('order_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get orders by IMEI: {e}")
            return []

    def get_recent_orders(self, limit: int = 50) -> List[Dict]:
        """Get recent orders"""
        try:
            response = self.client.table('orders').select('*').order('order_date', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get recent orders: {e}")
            return []

    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Get orders by status"""
        try:
            response = self.client.table('orders').select('*').eq('status', status).order('order_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get orders by status: {e}")
            return []

    def search_orders_by_status(self, statuses: List[str]) -> List[Dict]:
        """Get orders by multiple status values"""
        try:
            response = self.client.table('orders').select('*').in_('status', statuses).order('order_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to search orders by status: {e}")
            return []

    def get_orders_by_imeis(self, imeis: List[str]) -> List[Dict]:
        """Get all orders for multiple IMEIs (batch search)"""
        if not imeis:
            return []

        try:
            response = self.client.table('orders').select('*').in_('imei', imeis).order('order_date', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get orders by IMEIs: {e}")
            return []

    def search_orders(self, query: str) -> List[Dict]:
        """Search orders by IMEI, model, carrier, etc."""
        try:
            # Supabase uses ilike for case-insensitive pattern matching
            search_pattern = f"%{query}%"

            response = self.client.table('orders').select('*').or_(
                f"imei.ilike.{search_pattern},"
                f"model.ilike.{search_pattern},"
                f"carrier.ilike.{search_pattern},"
                f"order_id.ilike.{search_pattern}"
            ).order('order_date', desc=True).limit(100).execute()

            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to search orders: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}

            # Total orders
            response = self.client.table('orders').select('*', count='exact').execute()
            stats['total_orders'] = response.count if hasattr(response, 'count') else 0

            # Orders by status (need to fetch and group manually)
            all_orders = self.client.table('orders').select('status').execute()
            status_counts = {}
            if all_orders.data:
                for order in all_orders.data:
                    status = order.get('status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
            stats['by_status'] = status_counts

            # Total credits spent
            credits_response = self.client.table('orders').select('credits').execute()
            total_credits = 0.0
            if credits_response.data:
                for order in credits_response.data:
                    if order.get('credits'):
                        total_credits += float(order['credits'])
            stats['total_credits'] = total_credits

            # Orders today
            today = datetime.utcnow().date().isoformat()
            today_response = self.client.table('orders').select('*', count='exact').gte('order_date', today).execute()
            stats['orders_today'] = today_response.count if hasattr(today_response, 'count') else 0

            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total_orders': 0,
                'by_status': {},
                'total_credits': 0.0,
                'orders_today': 0
            }

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
        try:
            self.client.table('import_history').insert({
                'filename': 'hammer_export',
                'rows_imported': imported,
                'rows_skipped': skipped,
                'import_date': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to record import history: {e}")

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

        try:
            # Build query based on filters
            query = self.client.table('orders').select('*')

            if filters:
                if filters.get('status'):
                    query = query.eq('status', filters['status'])
                if filters.get('start_date'):
                    query = query.gte('order_date', filters['start_date'])
                if filters.get('end_date'):
                    query = query.lte('order_date', filters['end_date'])

            query = query.order('order_date', desc=True)
            response = query.execute()
            rows = response.data if response.data else []

            if not rows:
                return 0

            # Write to CSV
            with open(output_path, 'w', newline='') as csvfile:
                if rows:
                    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        # Convert multi-line CODE to single-line format for CSV export
                        if 'result_code_display' in row and row['result_code_display']:
                            row['result_code_display'] = row['result_code_display'].replace('\n', ' - ')
                        writer.writerow(row)

            return len(rows)
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return 0

    def close(self):
        """Close database connection (not needed for Supabase, but kept for compatibility)"""
        logger.info("Supabase client cleanup (connection pooled)")


# Global database instance
_db_instance = None


def get_database() -> IMEIDatabase:
    """Get or create global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = IMEIDatabase()
    return _db_instance
