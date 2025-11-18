#!/usr/bin/env python3
"""
Auto-Parse Orders - Integrate IMEI Data Parser with Database

This script automatically parses the CODE/result_code field from orders
and populates individual columns in the database.

Usage:
    python3 auto_parse_orders.py           # Parse all orders
    python3 auto_parse_orders.py --new     # Parse only new/unparsed orders
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import our parser and database
from imei_data_parser import IMEIDataParser
from database_supabase import get_database

def parse_and_update_order(order, parser, db):
    """
    Parse an order's CODE field and update database with parsed fields

    Args:
        order: Order dict from database
        parser: IMEIDataParser instance
        db: Database instance

    Returns:
        bool: True if updated successfully
    """
    # Get the CODE field (result_code or result_code_display)
    raw_code = order.get('result_code') or order.get('result_code_display') or ''

    if not raw_code or len(raw_code) < 10:
        print(f"  ⊘ Order {order['order_id']}: No CODE to parse")
        return False

    # Parse the CODE
    try:
        parsed = parser.parse(raw_code)

        # Check if we got any data
        parsed_dict = parsed.to_dict()
        if not parsed_dict:
            print(f"  ⊘ Order {order['order_id']}: Could not parse CODE")
            return False

        # Update the database with parsed fields
        update_data = {}

        # Map parser fields to database columns
        field_mapping = {
            'model': 'model',
            'carrier': 'carrier',
            'simlock': 'simlock',
            'find_my_iphone': 'fmi',
            'imei2_number': 'imei2',
            'serial_number': 'serial_number',
            'meid_number': 'meid',
            'current_gsma_status': 'gsma_status',
            'estimated_purchase_date': 'purchase_date',
            'applecare_eligible': 'applecare',
            'next_tether_policy': 'tether_policy',
        }

        for parser_field, db_field in field_mapping.items():
            value = getattr(parsed, parser_field, None)
            if value:
                update_data[db_field] = value

        if not update_data:
            print(f"  ⊘ Order {order['order_id']}: No fields to update")
            return False

        # Update the database
        success = db.update_order_status(
            order_id=order['order_id'],
            status=order['status'],  # Keep existing status
            result_data=update_data
        )

        if success:
            fields_updated = ', '.join(update_data.keys())
            print(f"  ✓ Order {order['order_id']}: Updated {len(update_data)} fields ({fields_updated})")
            return True
        else:
            print(f"  ✗ Order {order['order_id']}: Database update failed")
            return False

    except Exception as e:
        print(f"  ✗ Order {order['order_id']}: Error - {e}")
        return False


def parse_all_orders(only_unparsed=False):
    """
    Parse all orders in the database

    Args:
        only_unparsed: If True, only parse orders without model/carrier data
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🔍 AUTO-PARSE ORDERS - Populate Database Columns")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # Get database
    db = get_database()

    if not db.use_supabase:
        print("⚠️  Warning: Using SQLite, not Supabase")
        print("   Set SUPABASE_URL in .env to use Supabase")
        print()

    # Initialize parser
    parser = IMEIDataParser()

    # Get all completed orders
    print("📊 Fetching orders from database...")
    orders = db.get_orders_by_status('Completed')

    if not orders:
        print("⊘ No completed orders found")
        return

    print(f"Found {len(orders)} completed orders")
    print()

    # Filter if only unparsed
    if only_unparsed:
        orders_to_parse = [o for o in orders if not o.get('model') or not o.get('carrier')]
        print(f"Filtering to {len(orders_to_parse)} unparsed orders (no model/carrier)")
    else:
        orders_to_parse = orders
        print(f"Processing all {len(orders_to_parse)} orders")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # Parse each order
    updated = 0
    skipped = 0
    failed = 0

    for i, order in enumerate(orders_to_parse, 1):
        print(f"[{i}/{len(orders_to_parse)}] Processing order {order['order_id']}...")

        result = parse_and_update_order(order, parser, db)

        if result:
            updated += 1
        elif result is False:
            skipped += 1
        else:
            failed += 1

    # Summary
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📊 SUMMARY")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Total orders processed: {len(orders_to_parse)}")
    print(f"  ✓ Successfully updated:  {updated}")
    print(f"  ⊘ Skipped (no data):     {skipped}")
    print(f"  ✗ Failed:                {failed}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    if updated > 0:
        print("✅ Success! Check Supabase dashboard to see parsed columns.")
        print("   Go to: Table Editor → orders")
        print("   Columns now populated: model, carrier, simlock, fmi, etc.")
    else:
        print("⚠️  No orders were updated. Check that orders have CODE data.")


def parse_single_order(order_id):
    """Parse a single order by order_id"""
    print(f"🔍 Parsing order: {order_id}")

    db = get_database()
    parser = IMEIDataParser()

    # Get the order
    orders = db.get_orders_by_status('Completed')
    order = next((o for o in orders if o['order_id'] == order_id), None)

    if not order:
        print(f"❌ Order {order_id} not found or not completed")
        return False

    return parse_and_update_order(order, parser, db)


if __name__ == "__main__":
    import argparse

    parser_cli = argparse.ArgumentParser(
        description='Auto-parse IMEI order CODE fields into database columns'
    )
    parser_cli.add_argument(
        '--new',
        action='store_true',
        help='Only parse orders without model/carrier data'
    )
    parser_cli.add_argument(
        '--order-id',
        type=str,
        help='Parse a specific order by ID'
    )

    args = parser_cli.parse_args()

    if args.order_id:
        parse_single_order(args.order_id)
    else:
        parse_all_orders(only_unparsed=args.new)
