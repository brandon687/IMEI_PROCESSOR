#!/usr/bin/env python3
"""
Fetch missing order #15579051 from Hammer API and save to database
"""

import sys
sys.path.insert(0, '/Users/brandonin/Desktop/HAMMER-API')

from dotenv import load_dotenv
load_dotenv()

from gsm_fusion_client import GSMFusionClient
from database import get_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_save_order(order_id):
    """Fetch order from Hammer API and save to database"""

    logger.info(f"Fetching order #{order_id} from Hammer API...")

    # Create client
    client = GSMFusionClient()

    try:
        # Fetch order details
        orders = client.get_imei_orders(order_id)

        if not orders:
            logger.error(f"Order #{order_id} not found in Hammer API")
            return False

        order = orders[0]
        logger.info(f"Found order: {order.imei} - Status: {order.status}")

        # Get database
        db = get_database()

        # Prepare order data for database
        order_data = {
            'order_id': order.id,
            'service_name': order.package,
            'service_id': order.package_id if hasattr(order, 'package_id') else None,
            'imei': order.imei,
            'imei2': order.imei2 if hasattr(order, 'imei2') else None,
            'credits': order.price if hasattr(order, 'price') else None,
            'status': order.status,
            'carrier': None,  # Will be populated when order completes
            'simlock': None,
            'model': None,
            'fmi': None,
            'order_date': order.requested_at,
            'result_code': order.code if hasattr(order, 'code') else None,
            'notes': None,
            'raw_response': None
        }

        # Insert into database
        result = db.insert_order(order_data)

        if result:
            logger.info(f"✓ Successfully saved order #{order_id} to database (row {result})")
            return True
        else:
            logger.error(f"✗ Failed to save order #{order_id} to database")
            return False

    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

if __name__ == '__main__':
    order_id = '15579051'
    success = fetch_and_save_order(order_id)

    if success:
        print(f"\n✓ Order #{order_id} retrieved and saved successfully!")
        print(f"  IMEI: 357896548987478")
        print(f"  Check: http://localhost:5001/history")
    else:
        print(f"\n✗ Failed to retrieve order #{order_id}")
        sys.exit(1)
