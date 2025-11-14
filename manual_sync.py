#!/usr/bin/env python3
"""
Manual sync trigger - runs auto-sync logic once immediately
"""

import sys
import re
import os
from dotenv import load_dotenv
from database import IMEIDatabase
from gsm_fusion_client import GSMFusionClient

# Load environment variables
load_dotenv()

def manual_sync():
    """Manually trigger auto-sync for pending orders"""
    print("🔄 Starting manual sync...")

    db = IMEIDatabase()

    # Get all pending orders
    pending_orders = db.search_orders_by_status(['Pending', 'In Process', 'pending', 'in process'])

    if not pending_orders:
        print("✓ No pending orders to sync")
        return

    order_ids = [order['order_id'] for order in pending_orders if order.get('order_id')]
    print(f"Found {len(order_ids)} pending order(s): {order_ids}")

    # Fetch from GSM Fusion API
    client = GSMFusionClient()
    updated_orders = client.get_imei_orders(order_ids)
    client.close()

    print(f"Retrieved {len(updated_orders)} order(s) from API")

    # Update database with cleaned data
    updated_count = 0
    for api_order in updated_orders:
        result_data = {}
        cleaned_code = None

        if api_order.code:
            code_text = api_order.code

            # Helper function to clean HTML tags
            def clean_html(text):
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('<br>', '').replace('&lt;', '<').replace('&gt;', '>')
                return text.strip()

            # Clean the entire CODE field for display (multi-line format)
            cleaned_code = code_text.replace('<br>', '\n').replace('&lt;br&gt;', '\n')
            cleaned_code = re.sub(r'<[^>]+>', '', cleaned_code)
            cleaned_code = cleaned_code.replace('&lt;', '<').replace('&gt;', '>')
            cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)  # Remove blank lines
            cleaned_code = cleaned_code.strip()

            # Extract individual fields
            if 'Carrier:' in code_text:
                carrier = code_text.split('Carrier:')[1].split('<br>')[0].strip()
                result_data['carrier'] = clean_html(carrier)

            if 'SimLock:' in code_text or 'SIM Lock:' in code_text:
                simlock_key = 'SimLock:' if 'SimLock:' in code_text else 'SIM Lock:'
                simlock = code_text.split(simlock_key)[1].split('<br>')[0].strip()
                result_data['simlock'] = clean_html(simlock)

            if 'Model:' in code_text:
                model = code_text.split('Model:')[1].split('<br>')[0].strip()
                result_data['model'] = clean_html(model)

            if 'Find My iPhone:' in code_text or 'FMI:' in code_text:
                fmi_key = 'Find My iPhone:' if 'Find My iPhone:' in code_text else 'FMI:'
                fmi = code_text.split(fmi_key)[1].split('<br>')[0].strip()
                result_data['fmi'] = clean_html(fmi)

            if 'IMEI2 Number:' in code_text or 'IMEI 2:' in code_text:
                imei2_key = 'IMEI2 Number:' if 'IMEI2 Number:' in code_text else 'IMEI 2:'
                imei2 = code_text.split(imei2_key)[1].split('<br>')[0].strip()
                result_data['imei2'] = clean_html(imei2)

            # Store ORIGINAL for record keeping, CLEANED for display
            result_data['result_code'] = api_order.code
            result_data['result_code_display'] = cleaned_code

        # Update database
        db.update_order_status(
            order_id=api_order.id,
            status=api_order.status,
            code=api_order.code,  # Original with HTML
            code_display=cleaned_code,  # Cleaned for display
            service_name=api_order.package,  # Service name from API
            result_data=result_data if result_data else None
        )
        updated_count += 1
        print(f"  ✓ Updated order {api_order.id} → {api_order.status}")

    print(f"\n✅ Manual sync complete: Updated {updated_count} order(s)")

    # Show the results
    if updated_count > 0:
        print("\n" + "="*80)
        print("DATABASE VERIFICATION:")
        print("="*80)
        for order_id in order_ids[:1]:  # Show first order details
            import sqlite3
            conn = sqlite3.connect('imei_orders.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT order_id, status,
                       SUBSTR(result_code, 1, 150) as orig_preview,
                       SUBSTR(result_code_display, 1, 150) as display_preview
                FROM orders WHERE order_id = ?
            ''', (order_id,))
            row = cursor.fetchone()
            if row:
                print(f"\nOrder ID: {row[0]}")
                print(f"Status: {row[1]}")
                print(f"\nOriginal CODE (with HTML, first 150 chars):")
                print(f"  {row[2]}...")
                print(f"\nDisplay CODE (cleaned, first 150 chars):")
                print(f"  {row[3]}...")
            conn.close()

if __name__ == '__main__':
    manual_sync()
