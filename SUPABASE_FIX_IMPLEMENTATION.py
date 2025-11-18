"""
SUPABASE INTEGRATION FIX - Complete Implementation
==================================================

This file contains all the missing pieces to make Supabase sync work properly.
Apply these changes to web_app.py to enable full cloud sync.

Missing Components Fixed:
1. Result data parser (extract carrier, model, simlock from CODE field)
2. Enhanced order insertion (store full data on submission)
3. Background auto-sync thread (5-minute polling)
4. Enhanced manual sync (parse and store full results)

Instructions:
1. Backup web_app.py: cp web_app.py web_app.py.backup
2. Change line 10: from database import get_database  →  from database_supabase import get_database
3. Add parse_result_code() function (section A below)
4. Replace order insertion in /submit route (section B)
5. Replace order insertion in /submit-stream route (section C)
6. Replace order insertion in /batch route (section D)
7. Replace /history/sync route (section E)
8. Add background sync functions (section F)
9. Update if __name__ == '__main__': section (section G)
"""

import re
import json
import threading
import time
from typing import Dict


# ============================================================================
# SECTION A: Result Data Parser Function
# ============================================================================
# Add this function after the imports in web_app.py (around line 45)

def parse_result_code(code_html: str) -> Dict[str, str]:
    """
    Parse GSM Fusion CODE field (HTML) to extract structured data.

    The API returns results in HTML format like:
        "Carrier: T-Mobile<br/>Model: iPhone 12<br/>Simlock: Unlocked"

    This function extracts:
    - carrier: Carrier name (e.g., "T-Mobile", "Verizon")
    - model: Device model (e.g., "iPhone 12 Pro", "iPhone XS Max")
    - simlock: Lock status (e.g., "Unlocked", "Locked", "Unknown")
    - fmi: Find My iPhone status (e.g., "ON", "OFF", "Unknown")
    - imei2: Secondary IMEI for dual-SIM devices

    Args:
        code_html: Raw CODE string from API (may contain HTML tags)

    Returns:
        Dictionary with extracted fields (empty dict if parsing fails)

    Example:
        >>> parse_result_code("Carrier: T-Mobile<br/>Model: iPhone 12<br/>Simlock: Unlocked")
        {'carrier': 'T-Mobile', 'model': 'iPhone 12', 'simlock': 'Unlocked'}
    """
    if not code_html:
        return {}

    # Remove HTML tags and normalize spacing
    clean_code = re.sub(r'<[^>]+>', '\n', code_html)
    clean_code = re.sub(r'\s+', ' ', clean_code)

    # Extract key-value pairs using regex patterns
    results = {}

    patterns = {
        'carrier': r'(?:Carrier|Network|Provider)[:\s]+([^\n,]+?)(?:\n|$|<br|,)',
        'model': r'(?:Model|Device)[:\s]+([^\n,]+?)(?:\n|$|<br|,)',
        'simlock': r'(?:Simlock|Lock Status|Lock)[:\s]+([^\n,]+?)(?:\n|$|<br|,)',
        'fmi': r'(?:Find My iPhone|FMI|iCloud|Find My)[:\s]+([^\n,]+?)(?:\n|$|<br|,)',
        'imei2': r'(?:IMEI ?2|Secondary IMEI)[:\s]+([^\n,]+?)(?:\n|$|<br|,)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, clean_code, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Clean up common HTML entities
            value = value.replace('&nbsp;', ' ').replace('&amp;', '&')
            results[key] = value

    return results


# ============================================================================
# SECTION B: Enhanced Order Insertion for /submit Route
# ============================================================================
# Replace the order insertion code in /submit route (around line 480-500)
# Look for: "# Store in database" and replace the entire block with:

"""
        # Store in database with FULL data extraction
        db = get_db_safe()
        if db and result['orders']:
            service_name = get_service_name_by_id(service_id)
            logger.info(f"Storing {len(result['orders'])} orders in database")

            for i, order in enumerate(result['orders'], 1):
                try:
                    # Parse result data from CODE field if available
                    code = order.get('code', '')
                    result_data = parse_result_code(code) if code else {}

                    # Clean CODE for display (remove HTML tags)
                    code_display = re.sub(r'<[^>]+>', ' - ', code).strip() if code else None

                    # Prepare complete order data
                    order_data = {
                        'order_id': order['id'],
                        'imei': order['imei'],
                        'service_id': service_id,
                        'service_name': service_name,
                        'status': order.get('status', 'Pending'),
                        'credits': order.get('credits'),
                        'order_date': order.get('requested_at'),
                        'carrier': result_data.get('carrier') or order.get('carrier'),
                        'model': result_data.get('model') or order.get('model'),
                        'simlock': result_data.get('simlock') or order.get('simlock'),
                        'fmi': result_data.get('fmi') or order.get('fmi'),
                        'imei2': result_data.get('imei2') or order.get('imei2'),
                        'result_code': code,
                        'result_code_display': code_display,
                        'raw_response': json.dumps(order)
                    }

                    logger.info(f"Inserting order {i}/{len(result['orders'])}: "
                               f"order_id={order['id']}, imei={order['imei']}, "
                               f"carrier={order_data['carrier']}, model={order_data['model']}")

                    db.insert_order(order_data)
                    logger.info(f"✓ Successfully inserted order {order['id']} to database")

                except Exception as e:
                    logger.error(f"❌ DB insert failed for order {order.get('id', 'unknown')}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
"""


# ============================================================================
# SECTION C: Enhanced Order Insertion for /submit-stream Route
# ============================================================================
# Replace the order insertion in /submit-stream route (around line 656-670)
# Look for: "# Step 4: Database storage" and replace the block with:

"""
            # Step 4: Database storage (80%)
            yield f"data: {json.dumps({'type': 'progress', 'step': 'saving', 'message': 'Saving orders to database...', 'percent': 80})}\\n\\n"

            saved_count = 0
            if db and result['orders']:
                service_name = get_service_name_by_id(service_id)

                for order in result['orders']:
                    try:
                        # Parse result data
                        code = order.get('code', '')
                        result_data = parse_result_code(code) if code else {}
                        code_display = re.sub(r'<[^>]+>', ' - ', code).strip() if code else None

                        order_data = {
                            'order_id': order['id'],
                            'imei': order['imei'],
                            'service_id': service_id,
                            'service_name': service_name,
                            'status': order.get('status', 'Pending'),
                            'credits': order.get('credits'),
                            'order_date': order.get('requested_at'),
                            'carrier': result_data.get('carrier') or order.get('carrier'),
                            'model': result_data.get('model') or order.get('model'),
                            'simlock': result_data.get('simlock') or order.get('simlock'),
                            'fmi': result_data.get('fmi') or order.get('fmi'),
                            'imei2': result_data.get('imei2'),
                            'result_code': code,
                            'result_code_display': code_display,
                            'raw_response': json.dumps(order)
                        }

                        db.insert_order(order_data)
                        saved_count += 1
                    except Exception as e:
                        logger.warning(f"[SSE] DB insert failed for order {order['id']}: {e}")

                logger.info(f"[SSE] Saved {saved_count}/{len(result['orders'])} order(s) to database")

            yield f"data: {json.dumps({'type': 'progress', 'step': 'saved', 'message': f'Saved {saved_count} order(s) to database', 'percent': 90})}\\n\\n"
            time.sleep(0.1)
"""


# ============================================================================
# SECTION D: Enhanced Order Insertion for /batch Route
# ============================================================================
# Replace order insertion in /batch route (around line 798-817)
# Look for: "# Store in database" and replace with:

"""
            # Store in database with full data extraction
            db = get_db_safe()
            if db and result['orders']:
                service_name = get_service_name_by_id(service_id)
                logger.info(f"Storing {len(result['orders'])} orders in database")

                for i, order in enumerate(result['orders'], 1):
                    try:
                        # Parse result data
                        code = order.get('code', '')
                        result_data = parse_result_code(code) if code else {}
                        code_display = re.sub(r'<[^>]+>', ' - ', code).strip() if code else None

                        order_data = {
                            'order_id': order['id'],
                            'imei': order['imei'],
                            'service_id': service_id,
                            'service_name': service_name,
                            'status': order.get('status', 'Pending'),
                            'credits': order.get('credits'),
                            'order_date': order.get('requested_at'),
                            'carrier': result_data.get('carrier') or order.get('carrier'),
                            'model': result_data.get('model') or order.get('model'),
                            'simlock': result_data.get('simlock') or order.get('simlock'),
                            'fmi': result_data.get('fmi') or order.get('fmi'),
                            'imei2': result_data.get('imei2'),
                            'result_code': code,
                            'result_code_display': code_display,
                            'raw_response': json.dumps(order)
                        }

                        logger.info(f"Inserting order {i}/{len(result['orders'])}: order_id={order['id']}, imei={order['imei']}")
                        db.insert_order(order_data)
                        logger.info(f"✓ Successfully inserted order {order['id']}")

                    except Exception as e:
                        logger.error(f"❌ DB insert failed for order {order.get('id', 'unknown')}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
"""


# ============================================================================
# SECTION E: Enhanced Manual Sync Route
# ============================================================================
# Replace entire /history/sync route (around line 899-977) with:

"""
@app.route('/history/sync', methods=['GET'])
@error_handler
def sync_orders():
    \"\"\"Sync pending orders with API to update their status and extract full results\"\"\"
    logger.info("SYNC route called")

    db = get_db_safe()
    if not db:
        flash('Database not available', 'error')
        return redirect(url_for('history'))

    try:
        # Get all pending orders using proper method
        if hasattr(db, 'search_orders_by_status'):
            pending_orders = db.search_orders_by_status(['Pending', 'In Process', '1', '4'])
        else:
            pending_orders = db.get_orders_by_status('Pending')

        if not pending_orders:
            flash('No pending orders to sync', 'info')
            return redirect(url_for('history'))

        # Collect order IDs
        order_ids = [order['order_id'] for order in pending_orders]
        logger.info(f"Syncing {len(order_ids)} pending orders")

        # Fetch status from API (batch)
        client = GSMFusionClient(timeout=30)
        updated_count = 0

        try:
            # API accepts comma-separated order IDs for batch lookup
            order_ids_str = ','.join(order_ids)
            updated_orders = client.get_imei_orders(order_ids_str)

            # Update database with full parsed results
            for order in updated_orders:
                try:
                    # Parse result data from CODE field
                    code = order.code or ''
                    result_data = parse_result_code(code) if code else {}
                    code_display = re.sub(r'<[^>]+>', ' - ', code).strip() if code else None

                    # Merge API data with parsed data
                    merged_result_data = {
                        'carrier': result_data.get('carrier') or order.carrier,
                        'model': result_data.get('model') or order.model,
                        'simlock': result_data.get('simlock') or order.simlock,
                        'fmi': result_data.get('fmi') or order.fmi,
                        'imei2': result_data.get('imei2'),
                        'service_name': order.package
                    }

                    # Update order with complete data
                    db.update_order_status(
                        order_id=order.id,
                        status=order.status,
                        result_code=code,
                        result_code_display=code_display,
                        result_data=merged_result_data
                    )
                    updated_count += 1

                    logger.info(f"✅ Updated order {order.id}: status={order.status}, "
                               f"carrier={merged_result_data.get('carrier')}, "
                               f"model={merged_result_data.get('model')}")

                except Exception as e:
                    logger.warning(f"Failed to update order {order.id}: {e}")

            flash(f'✅ Synced {updated_count} orders successfully', 'success')

        except Exception as e:
            logger.error(f"API sync failed: {e}")
            logger.error(traceback.format_exc())
            flash(f'Sync failed: {str(e)}', 'error')
        finally:
            client.close()

        return redirect(url_for('history'))

    except Exception as e:
        logger.error(f"Sync error: {e}")
        logger.error(traceback.format_exc())
        flash(f'Sync failed: {str(e)}', 'error')
        return redirect(url_for('history'))
"""


# ============================================================================
# SECTION F: Background Auto-Sync Functions
# ============================================================================
# Add these functions BEFORE the "if __name__ == '__main__':" section (around line 1395)

"""
def background_sync_thread():
    \"\"\"
    Background thread that auto-syncs pending orders periodically.

    This thread runs continuously in the background, checking for pending
    orders and syncing them with the GSM Fusion API to get updated results.

    Features:
    - Configurable sync interval (default: 5 minutes)
    - Handles both Supabase and SQLite databases
    - Automatic result parsing and extraction
    - Error handling with retry logic
    - Non-blocking (runs as daemon thread)

    Environment Variables:
        AUTO_SYNC_INTERVAL: Seconds between sync runs (default: 300)
        DISABLE_AUTO_SYNC: Set to 'true' to disable auto-sync
    \"\"\"
    sync_interval = int(os.environ.get('AUTO_SYNC_INTERVAL', 300))  # Default 5 minutes

    logger.info(f"🔄 Auto-sync thread started (interval: {sync_interval}s = {sync_interval//60} minutes)")

    while True:
        try:
            time.sleep(sync_interval)

            db = get_db_safe()
            if not db:
                logger.warning("Auto-sync: Database not available, skipping this cycle")
                continue

            # Get pending orders based on database type
            order_ids = []

            if db.use_supabase:
                # Supabase query for pending orders
                try:
                    response = db.supabase_client.table('orders') \\
                        .select('order_id') \\
                        .in_('status', ['Pending', 'In Process', '1', '4']) \\
                        .execute()
                    pending_orders = response.data if response.data else []
                    order_ids = [o['order_id'] for o in pending_orders]
                except Exception as e:
                    logger.error(f"Auto-sync: Failed to query Supabase: {e}")
                    continue
            else:
                # SQLite query for pending orders
                try:
                    cursor = db.conn.cursor()
                    cursor.execute("SELECT order_id FROM orders WHERE status IN ('Pending', 'In Process', '1', '4')")
                    order_ids = [row[0] for row in cursor.fetchall()]
                except Exception as e:
                    logger.error(f"Auto-sync: Failed to query SQLite: {e}")
                    continue

            if not order_ids:
                logger.info("Auto-sync: No pending orders to sync")
                continue

            logger.info(f"Auto-sync: Found {len(order_ids)} pending orders, fetching updates from API...")

            # Fetch updates from GSM Fusion API
            client = GSMFusionClient(timeout=30)

            try:
                # API accepts comma-separated order IDs
                order_ids_str = ','.join(order_ids)
                updated_orders = client.get_imei_orders(order_ids_str)

                # Update database with parsed results
                update_count = 0
                for order in updated_orders:
                    try:
                        # Parse result data from CODE field
                        code = order.code or ''
                        result_data = parse_result_code(code) if code else {}
                        code_display = re.sub(r'<[^>]+>', ' - ', code).strip() if code else None

                        # Merge API fields with parsed fields
                        merged_data = {
                            'carrier': result_data.get('carrier') or order.carrier,
                            'model': result_data.get('model') or order.model,
                            'simlock': result_data.get('simlock') or order.simlock,
                            'fmi': result_data.get('fmi') or order.fmi,
                            'imei2': result_data.get('imei2'),
                            'service_name': order.package
                        }

                        # Update order in database
                        success = db.update_order_status(
                            order_id=order.id,
                            status=order.status,
                            result_code=code,
                            result_code_display=code_display,
                            result_data=merged_data
                        )

                        if success:
                            update_count += 1
                            logger.info(f"Auto-sync: Updated {order.id} - {order.status} - {merged_data.get('carrier')}")

                    except Exception as e:
                        logger.warning(f"Auto-sync: Failed to update order {order.id}: {e}")

                logger.info(f"✅ Auto-sync: Successfully updated {update_count}/{len(updated_orders)} orders")

            except Exception as e:
                logger.error(f"Auto-sync: API request failed: {e}")
                logger.error(traceback.format_exc())
            finally:
                client.close()

        except Exception as e:
            logger.error(f"Auto-sync thread error: {e}")
            logger.error(traceback.format_exc())
            # Continue running despite errors


def start_auto_sync():
    \"\"\"
    Start background auto-sync thread.

    Creates and starts a daemon thread for automatic order syncing.
    Daemon threads automatically terminate when the main program exits.

    Can be disabled by setting DISABLE_AUTO_SYNC=true in environment.
    \"\"\"
    if os.environ.get('DISABLE_AUTO_SYNC', '').lower() == 'true':
        logger.info("⚠️  Background auto-sync DISABLED (DISABLE_AUTO_SYNC=true)")
        return

    try:
        sync_thread = threading.Thread(target=background_sync_thread, daemon=True)
        sync_thread.start()
        logger.info("✅ Background auto-sync enabled and running")
        logger.info(f"   Sync interval: {os.environ.get('AUTO_SYNC_INTERVAL', '300')}s")
    except Exception as e:
        logger.error(f"Failed to start auto-sync thread: {e}")
        logger.warning("Continuing without auto-sync - manual sync still available")
"""


# ============================================================================
# SECTION G: Update Main Entry Point
# ============================================================================
# Replace the "if __name__ == '__main__':" section (around line 1395-1410) with:

"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))

    # Pre-warm cache on startup
    logger.info("=" * 60)
    logger.info("Starting HAMMER-API Web Application...")
    logger.info("=" * 60)

    logger.info("Pre-warming services cache...")
    try:
        services = get_services_cached()
        logger.info(f"✓ Cache warmed with {len(services)} services")
    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")
        logger.warning("Continuing anyway - cache will populate on first request")

    # Check database connection
    logger.info("Checking database connection...")
    try:
        db = get_db_safe()
        if db:
            if db.use_supabase:
                logger.info("✓ Database: Supabase (cloud)")
            else:
                logger.info("✓ Database: SQLite (local)")
        else:
            logger.warning("⚠️  Database not available - some features may be limited")
    except Exception as e:
        logger.error(f"Database check failed: {e}")

    # Start background auto-sync thread
    logger.info("Starting background auto-sync...")
    start_auto_sync()

    logger.info("=" * 60)
    logger.info(f"🚀 Flask server starting on port {port}")
    logger.info(f"   Access at: http://localhost:{port}")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=False)
"""


# ============================================================================
# DEPLOYMENT NOTES
# ============================================================================

DEPLOYMENT_NOTES = """
DEPLOYMENT CHECKLIST
====================

1. CHANGE DATABASE IMPORT (CRITICAL)
   ✓ Edit web_app.py line 10
   ✓ Change: from database import get_database
   ✓ To:     from database_supabase import get_database

2. SET ENVIRONMENT VARIABLES
   ✓ SUPABASE_URL=https://xxxxx.supabase.co
   ✓ SUPABASE_KEY=eyJhbGc...
   ✓ AUTO_SYNC_INTERVAL=300 (optional, default 5 minutes)

3. VERIFY SUPABASE TABLES
   ✓ Run supabase_schema.sql in Supabase SQL Editor
   ✓ Check that 'orders' table exists
   ✓ Verify indexes are created

4. TEST LOCALLY FIRST
   ✓ python3 web_app.py
   ✓ Submit test IMEI
   ✓ Check logs for "✓ Connected to Supabase"
   ✓ Verify auto-sync starts
   ✓ Check Supabase dashboard for data

5. DEPLOY TO RAILWAY
   ✓ Set environment variables in Railway dashboard
   ✓ Deploy updated code
   ✓ Check deployment logs
   ✓ Test submission and verify data appears in Supabase

6. MONITOR
   ✓ Check logs for "Auto-sync: Updated X orders"
   ✓ Verify pending orders become completed
   ✓ Confirm carrier/model data appears

TROUBLESHOOTING
===============

If data not appearing in Supabase:
→ Check web_app.py line 10 imports database_supabase
→ Verify SUPABASE_URL and SUPABASE_KEY are set
→ Check logs for "Connected to Supabase"
→ Verify tables exist in Supabase dashboard

If auto-sync not working:
→ Check logs for "Auto-sync thread started"
→ Verify AUTO_SYNC_INTERVAL is set (default 300s)
→ Check for "Auto-sync: Updated X orders" in logs
→ Ensure DISABLE_AUTO_SYNC is not set to 'true'

If missing result data:
→ Verify parse_result_code() function is added
→ Check logs for "carrier=..., model=..." during insertion
→ Run manual sync to update existing orders
→ Check Supabase table for populated carrier/model fields

TESTING COMMANDS
================

# Test database connection
python3 -c "from database_supabase import get_database; db = get_database(); print(f'Supabase: {db.use_supabase}')"

# Test result parser
python3 -c "from web_app import parse_result_code; print(parse_result_code('Carrier: T-Mobile<br/>Model: iPhone 12'))"

# Check pending orders
python3 -c "from database_supabase import get_database; db = get_database(); orders = db.search_orders_by_status(['Pending']); print(f'{len(orders)} pending')"
"""

print(DEPLOYMENT_NOTES)
