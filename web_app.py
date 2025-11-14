#!/usr/bin/env python3
"""
GSM Fusion Web Interface
Local web app for testing IMEI submissions and viewing results
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError
from database import get_database
from production_submission_system import ProductionSubmissionSystem, SubmissionResult
import os
import csv
import io
import openpyxl
from datetime import datetime
import threading
import time as time_module
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store recent orders in session
RECENT_ORDERS = []

# Initialize database
db = get_database()

# Auto-sync configuration
AUTO_SYNC_ENABLED = True
AUTO_SYNC_INTERVAL = 300  # 5 minutes in seconds


@app.route('/')
def index():
    """Home page with service list"""
    try:
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        # Get popular services (first 20)
        popular_services = services[:20]

        return render_template('index.html',
                             services=popular_services,
                             total_services=len(services),
                             recent_orders=RECENT_ORDERS)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/services')
def services():
    """Full services list page"""
    try:
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        # Filter by category if provided
        category = request.args.get('category')
        search = request.args.get('search', '').lower()

        if category:
            services = [s for s in services if s.category == category]

        if search:
            services = [s for s in services if search in s.title.lower() or search in s.category.lower()]

        # Get unique categories
        categories = list(set([s.category for s in services]))

        return render_template('services.html',
                             services=services,
                             categories=categories,
                             selected_category=category,
                             search=search)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    """Submit order page"""
    if request.method == 'POST':
        try:
            imei_input = request.form.get('imei')
            service_id = request.form.get('service_id')
            force_recheck = request.form.get('force_recheck') == 'true'

            if not imei_input or not service_id:
                flash('IMEI and Service ID are required', 'error')
                return redirect(url_for('submit'))

            # Parse multiple IMEIs (one per line)
            imei_lines = imei_input.strip().split('\n')
            imeis = []
            for line in imei_lines:
                imei = line.strip()
                if imei:  # Skip empty lines
                    # Validate IMEI
                    if not imei.isdigit() or len(imei) != 15:
                        flash(f'Invalid IMEI: {imei}. Must be 15 digits. Skipped.', 'warning')
                        continue
                    imeis.append(imei)

            if not imeis:
                flash('No valid IMEIs found. Each IMEI must be 15 digits.', 'error')
                return redirect(url_for('submit'))

            # Use production-grade submission system with individual API calls
            # NOTE: GSM Fusion API does NOT support batch submission (tested 2025-11-14)
            # Using batch_size=1 with 30 workers = 30 concurrent individual calls
            system = ProductionSubmissionSystem(
                database_path='imei_orders.db',
                batch_size=1,    # Individual API calls (batch not supported by GSM Fusion)
                max_workers=30,  # 30 concurrent submissions
                max_retries=3,   # Retry failed submissions up to 3 times
                enable_checkpointing=True  # Save progress for crash recovery
            )

            # Submit batch with production system
            result = system.submit_batch(imeis, service_id, force_recheck=force_recheck)

            # Update RECENT_ORDERS for UI display (last 10 successful orders)
            for order in result.orders[:10]:
                RECENT_ORDERS.insert(0, {
                    'order_id': order.get('order_id'),
                    'imei': order.get('imei'),
                    'service_id': service_id,
                    'status': order.get('status'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            # Keep only last 10 orders
            while len(RECENT_ORDERS) > 10:
                RECENT_ORDERS.pop()

            # Extract order IDs for potential redirect
            order_ids = [o.get('order_id') for o in result.orders if o.get('order_id')]

            # Show summary with performance metrics
            summary_msg = (
                f'Processed {result.total} IMEI(s) in {result.duration_seconds:.1f} seconds: '
                f'{result.successful} successful ({result.success_rate():.1f}%), '
                f'{result.duplicates} duplicates, {result.failed} errors'
            )

            # Add warning if any failures occurred
            if result.failed > 0:
                summary_msg += f' | {len(result.errors)} errors logged'

            # Determine flash message type and redirect
            if result.success_rate() >= 95:
                flash(summary_msg, 'success')
                # Redirect to first order if only one, otherwise to history
                if result.successful == 1 and order_ids:
                    return redirect(url_for('order_status', order_id=order_ids[0]))
                else:
                    return redirect(url_for('history'))
            elif result.success_rate() >= 70:
                flash(f'{summary_msg}. Some submissions failed - check history for details.', 'warning')
                return redirect(url_for('history'))
            elif result.duplicates > 0 and result.successful == 0:
                flash(f'{summary_msg}. All IMEIs were duplicates.', 'warning')
                return redirect(url_for('submit'))
            else:
                flash(f'{summary_msg}. Most submissions failed - check logs for details.', 'error')
                return redirect(url_for('submit'))

        except GSMFusionAPIError as e:
            flash(f'API Error: {str(e)}', 'error')
            return redirect(url_for('submit'))

    # GET request - show form
    try:
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        # Get popular/recommended services
        recommended = [s for s in services if 'checker' in s.title.lower() or 'hot' in s.category.lower()][:10]

        return render_template('submit.html', services=recommended)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/status/<order_id>')
def order_status(order_id):
    """Check order status page"""
    try:
        # First try to get from local database
        db_order = db.get_order_by_id(order_id)

        if db_order:
            # Use database order which has cleaned result_code_display
            # Create an object-like structure for template compatibility
            class OrderView:
                def __init__(self, db_order):
                    self.id = db_order.get('order_id')
                    self.imei = db_order.get('imei')
                    self.package = db_order.get('service_name')
                    self.status = db_order.get('status')
                    self.requested_at = db_order.get('order_date')
                    # Use cleaned display version instead of original
                    self.code = db_order.get('result_code_display') or db_order.get('result_code')

            order = OrderView(db_order)
        else:
            # Fallback: fetch from GSM Fusion API
            client = GSMFusionClient()
            orders = client.get_imei_orders(order_id)
            client.close()

            if not orders:
                flash('Order not found', 'error')
                return redirect(url_for('index'))

            order = orders[0]

        return render_template('status.html', order=order)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/api/check_status/<order_id>')
def api_check_status(order_id):
    """API endpoint for checking order status (for auto-refresh)"""
    try:
        client = GSMFusionClient()
        orders = client.get_imei_orders(order_id)
        client.close()

        if not orders:
            return jsonify({'error': 'Order not found'}), 404

        order = orders[0]

        return jsonify({
            'order_id': order.id,
            'imei': order.imei,
            'status': order.status,
            'package': order.package,
            'code': order.code,
            'requested_at': order.requested_at
        })
    except GSMFusionAPIError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/batch', methods=['GET', 'POST'])
def batch_upload():
    """Batch upload CSV file with IMEIs"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'csv_file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('batch_upload'))

            file = request.files['csv_file']

            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('batch_upload'))

            if not file.filename.endswith('.csv'):
                flash('File must be a CSV file', 'error')
                return redirect(url_for('batch_upload'))

            # Get service ID
            service_id = request.form.get('service_id')
            if not service_id:
                flash('Please select a service', 'error')
                return redirect(url_for('batch_upload'))

            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.reader(stream)

            # Read all rows
            rows = list(csv_reader)

            if len(rows) < 2:
                flash('CSV file must have at least a header and one IMEI', 'error')
                return redirect(url_for('batch_upload'))

            # Check header (should be "IMEI" in first column)
            header = rows[0]
            if not header or header[0].strip().upper() != 'IMEI':
                flash('CSV must have "IMEI" as header in column A (row 1)', 'error')
                return redirect(url_for('batch_upload'))

            # Extract IMEIs from column A (skipping header)
            imeis = []
            for i, row in enumerate(rows[1:], start=2):
                if row and len(row) > 0 and row[0].strip():
                    imei = row[0].strip()
                    # Validate IMEI format
                    if imei.isdigit() and len(imei) == 15:
                        imeis.append(imei)
                    else:
                        flash(f'Row {i}: Invalid IMEI "{imei}" - must be 15 digits', 'warning')

            if not imeis:
                flash('No valid IMEIs found in CSV file', 'error')
                return redirect(url_for('batch_upload'))

            # Use production-grade submission system with individual API calls
            # NOTE: GSM Fusion API does NOT support batch submission (tested 2025-11-14)
            # Using batch_size=1 with 30 workers = 30 concurrent individual calls
            system = ProductionSubmissionSystem(
                database_path='imei_orders.db',
                batch_size=1,    # Individual API calls (batch not supported by GSM Fusion)
                max_workers=30,  # 30 concurrent submissions
                max_retries=3,   # Retry failed submissions up to 3 times
                enable_checkpointing=True  # Save progress for crash recovery
            )

            # Submit batch with production system
            submission_result = system.submit_batch(imeis, service_id)

            # Update RECENT_ORDERS for UI display
            for order in submission_result.orders[:50]:
                RECENT_ORDERS.insert(0, {
                    'order_id': order.get('order_id'),
                    'imei': order.get('imei'),
                    'service_id': service_id,
                    'status': order.get('status'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            # Keep only last 50 orders
            if len(RECENT_ORDERS) > 50:
                RECENT_ORDERS = RECENT_ORDERS[:50]

            # Build results for template display
            results = []

            # Add successful orders
            for order in submission_result.orders:
                results.append({
                    'imei': order.get('imei'),
                    'status': 'success',
                    'order_id': order.get('order_id'),
                    'order_status': order.get('status'),
                    'message': f"Order {order.get('order_id')} created"
                })

            # Add duplicates
            for dup_imei in submission_result.duplicate_imeis:
                results.append({
                    'imei': dup_imei,
                    'status': 'duplicate',
                    'order_id': None,
                    'order_status': None,
                    'message': 'Duplicate IMEI - already submitted'
                })

            # Add errors
            for error in submission_result.errors:
                results.append({
                    'imei': error.get('imei', 'Unknown'),
                    'status': 'error',
                    'order_id': None,
                    'order_status': None,
                    'message': error.get('message', 'Unknown error')
                })

            # Show flash message with performance metrics
            flash(
                f'Processed {submission_result.total} IMEIs in {submission_result.duration_seconds:.1f} seconds: '
                f'{submission_result.successful} successful, {submission_result.failed} errors, '
                f'{submission_result.duplicates} duplicates',
                'success' if submission_result.success_rate() >= 95 else 'warning'
            )

            return render_template('batch_results.html', results=results, service_id=service_id)

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('batch_upload'))

    # GET request - show upload form
    try:
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        # Get popular services
        recommended = [s for s in services if 'checker' in s.title.lower() or 'hot' in s.category.lower()][:10]

        return render_template('batch_upload.html', services=recommended)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/history')
def history():
    """View recent order history from database with optional IMEI search (supports multiple IMEIs)"""
    try:
        # Get search query from URL parameters
        search_imei = request.args.get('imei', '').strip()

        # Get orders from database
        if search_imei:
            # Parse IMEIs - one per line (same format as submit order page)
            imeis = []
            for line in search_imei.split('\n'):
                imei = line.strip()
                if not imei:  # Skip empty lines
                    continue

                # Validate IMEI (must be 15 digits)
                if not imei.isdigit():
                    continue
                if len(imei) != 15:
                    continue

                imeis.append(imei)

            valid_imeis = imeis

            if len(valid_imeis) == 1:
                # Single IMEI search
                orders = db.get_orders_by_imei(valid_imeis[0])
            elif len(valid_imeis) > 1:
                # Multi-IMEI search
                orders = db.get_orders_by_imeis(valid_imeis)
            else:
                # No valid IMEIs found
                orders = []
                flash(f'No valid IMEIs found. Each IMEI must be 15 digits.', 'warning')
        else:
            # Get recent orders (persistent across restarts)
            orders = db.get_recent_orders(limit=100)

        # Convert database format to template format
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                'order_id': order.get('order_id', 'N/A'),
                'imei': order.get('imei', 'N/A'),
                'imei2': order.get('imei2', ''),
                'service_id': order.get('service_id', 'N/A'),
                'service_name': order.get('service_name', ''),
                'status': order.get('status', 'Unknown'),
                'timestamp': order.get('order_date', order.get('created_at', 'N/A')),
                'carrier': order.get('carrier', ''),
                'simlock': order.get('simlock', ''),
                'model': order.get('model', ''),
                'fmi': order.get('fmi', '')
            })

        # Calculate how many IMEIs were searched (one per line)
        search_count = 0
        if search_imei:
            for line in search_imei.split('\n'):
                imei = line.strip()
                if imei and imei.isdigit() and len(imei) == 15:
                    search_count += 1

        return render_template('history.html', orders=formatted_orders, search_query=search_imei, search_count=search_count)
    except Exception as e:
        flash(f'Error loading history: {str(e)}', 'error')
        return render_template('history.html', orders=[], search_query='')


@app.route('/history/export')
def history_export():
    """Export order history to CSV (supports multi-IMEI search)"""
    try:
        # Get search query from URL parameters
        search_imei = request.args.get('imei', '').strip()

        # Get orders from database
        if search_imei:
            # Parse IMEIs - one per line (same logic as history route)
            imeis = []
            for line in search_imei.split('\n'):
                imei = line.strip()
                if not imei:
                    continue
                if imei.isdigit() and len(imei) == 15:
                    imeis.append(imei)

            valid_imeis = imeis

            if len(valid_imeis) == 1:
                orders = db.get_orders_by_imei(valid_imeis[0])
                filename = f"orders_{valid_imeis[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            elif len(valid_imeis) > 1:
                orders = db.get_orders_by_imeis(valid_imeis)
                filename = f"orders_multi_{len(valid_imeis)}imeis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            else:
                flash('No valid IMEIs found', 'error')
                return redirect(url_for('history'))
        else:
            orders = db.get_recent_orders(limit=10000)  # Export up to 10,000 orders
            filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header (matching GSM Fusion "Advanced Export" format exactly)
        # NOTE: GSM Fusion does NOT include #ID in their exports
        writer.writerow([
            'SERVICE',
            'IMEI NO.',
            'CREDITS',
            'STATUS',
            'CODE',
            'IMEI 2',
            'CARRIER',
            'SIMLOCK',
            'MODEL',
            'FMI',
            'ORDER DATE',
            'NOTES'
        ])

        # Write data rows (matching GSM Fusion format)
        for order in orders:
            # Convert multi-line CODE to single-line format for CSV export
            code_display = order.get('result_code_display') or order.get('result_code', '')
            code_csv = code_display.replace('\n', ' - ') if code_display else ''

            writer.writerow([
                order.get('service_name', ''),
                order.get('imei', ''),
                f"${order.get('credits', 0.08):.2f}",  # Format as currency
                order.get('status', ''),
                code_csv,  # Single-line format with " - " separators for CSV
                order.get('imei2', ''),
                order.get('carrier', ''),
                order.get('simlock', ''),
                order.get('model', ''),
                order.get('fmi', ''),
                order.get('order_date', ''),
                order.get('notes', '')
            ])

        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        flash(f'Error exporting orders: {str(e)}', 'error')
        return redirect(url_for('history'))


@app.route('/history/sync')
def history_sync():
    """Sync order status from GSM Fusion API and update database"""
    try:
        # Get all pending/in-process orders from database
        pending_orders = db.search_orders_by_status(['Pending', 'In Process', 'pending', 'in process'])

        print(f"DEBUG: Found {len(pending_orders)} pending orders")
        for order in pending_orders:
            print(f"  - Order {order.get('order_id')}: {order.get('imei')} - {order.get('status')}")

        if not pending_orders:
            flash('No pending orders to sync', 'info')
            return redirect(url_for('history'))

        # Collect order IDs to sync
        order_ids = [order['order_id'] for order in pending_orders if order.get('order_id')]

        if not order_ids:
            flash('No valid order IDs found to sync', 'warning')
            return redirect(url_for('history'))

        # Fetch status from GSM Fusion API (supports batch)
        print(f"DEBUG: Fetching status for order IDs: {order_ids}")
        client = GSMFusionClient()
        updated_orders = client.get_imei_orders(order_ids)
        client.close()

        print(f"DEBUG: API returned {len(updated_orders)} orders")
        for order in updated_orders:
            print(f"  - API Order {order.id}: Status={order.status}, has code={bool(order.code)}")

        # Update database with latest status
        updated_count = 0
        for api_order in updated_orders:
            # Parse CODE field to extract individual fields
            result_data = {}
            if api_order.code:
                code_text = api_order.code

                # Extract Carrier
                if 'Carrier:' in code_text:
                    carrier = code_text.split('Carrier:')[1].split('-')[0].split('\n')[0].strip()
                    result_data['carrier'] = carrier

                # Extract SimLock
                if 'SimLock:' in code_text or 'SIM Lock:' in code_text:
                    simlock_key = 'SimLock:' if 'SimLock:' in code_text else 'SIM Lock:'
                    simlock = code_text.split(simlock_key)[1].split('-')[0].split('\n')[0].strip()
                    result_data['simlock'] = simlock

                # Extract Model
                if 'Model:' in code_text:
                    model = code_text.split('Model:')[1].split('-')[0].split('\n')[0].strip()
                    result_data['model'] = model

                # Extract FMI (Find My iPhone)
                if 'Find My iPhone:' in code_text or 'FMI:' in code_text:
                    fmi_key = 'Find My iPhone:' if 'Find My iPhone:' in code_text else 'FMI:'
                    fmi = code_text.split(fmi_key)[1].split('-')[0].split('\n')[0].strip()
                    result_data['fmi'] = fmi

                # Extract IMEI2
                if 'IMEI2 Number:' in code_text or 'IMEI 2:' in code_text:
                    imei2_key = 'IMEI2 Number:' if 'IMEI2 Number:' in code_text else 'IMEI 2:'
                    imei2 = code_text.split(imei2_key)[1].split('-')[0].split('\n')[0].strip()
                    result_data['imei2'] = imei2

                result_data['result_code'] = code_text

            # Update order in database with parsed data
            db.update_order_status(
                order_id=api_order.id,
                status=api_order.status,
                code=api_order.code,
                result_data=result_data if result_data else None
            )
            updated_count += 1

        flash(f'Successfully synced {updated_count} order(s) from GSM Fusion API', 'success')
        return redirect(url_for('history'))

    except GSMFusionAPIError as e:
        flash(f'API sync failed: {str(e)}', 'error')
        return redirect(url_for('history'))
    except Exception as e:
        flash(f'Sync error: {str(e)}', 'error')
        return redirect(url_for('history'))


@app.route('/service/<service_id>')
def service_detail(service_id):
    """View service details"""
    try:
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        # Find the service
        service = next((s for s in services if s.package_id == service_id), None)

        if not service:
            flash('Service not found', 'error')
            return redirect(url_for('services'))

        return render_template('service_detail.html', service=service)
    except GSMFusionAPIError as e:
        return render_template('error.html', error=str(e))


@app.route('/database')
def database_view():
    """View database statistics and recent orders"""
    try:
        stats = db.get_statistics()
        recent_orders = db.get_recent_orders(limit=20)

        return render_template('database.html',
                             stats=stats,
                             recent_orders=recent_orders)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/database/import', methods=['GET', 'POST'])
def database_import():
    """Import Hammer Fusion export file"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'excel_file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('database_import'))

            file = request.files['excel_file']

            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('database_import'))

            # Read Excel file
            wb = openpyxl.load_workbook(file)
            ws = wb.active

            # Get headers
            headers = [cell.value for cell in ws[1]]

            # Parse data rows
            excel_data = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if any(row):  # Skip completely empty rows
                    row_dict = {headers[i]: row[i] for i in range(len(headers))}
                    excel_data.append(row_dict)

            # Import to database
            result = db.import_from_hammer_export(excel_data)

            flash(f'Import complete: {result["imported"]} orders imported, {result["skipped"]} skipped', 'success')
            return redirect(url_for('database_view'))

        except Exception as e:
            flash(f'Import failed: {str(e)}', 'error')
            return redirect(url_for('database_import'))

    return render_template('database_import.html')


@app.route('/database/search')
def database_search():
    """Search database"""
    query = request.args.get('q', '')

    if not query:
        return redirect(url_for('database_view'))

    try:
        results = db.search_orders(query)
        return render_template('database_search.html',
                             query=query,
                             results=results)
    except Exception as e:
        flash(f'Search error: {str(e)}', 'error')
        return redirect(url_for('database_view'))


@app.route('/database/export')
def database_export():
    """Export database to CSV"""
    try:
        # Get filters from query parameters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')

        # Generate export filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'imei_orders_export_{timestamp}.csv'
        filepath = f'/tmp/{filename}'

        # Export to CSV
        count = db.export_to_csv(filepath, filters)

        if count == 0:
            flash('No orders to export', 'warning')
            return redirect(url_for('database_view'))

        return send_file(filepath,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='text/csv')

    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('database_view'))


@app.route('/database/order/<order_id>')
def database_order_detail(order_id):
    """View order details from database"""
    try:
        order = db.get_order_by_id(order_id)

        if not order:
            flash('Order not found in database', 'error')
            return redirect(url_for('database_view'))

        return render_template('database_order_detail.html', order=order)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('database_view'))


def auto_sync_orders():
    """Background task to automatically sync pending orders from GSM Fusion API"""
    logger.info("🔄 Auto-sync service started")

    while AUTO_SYNC_ENABLED:
        try:
            # Get all pending/in-process orders from database
            pending_orders = db.search_orders_by_status(['Pending', 'In Process', 'pending', 'in process'])

            if pending_orders:
                order_ids = [order['order_id'] for order in pending_orders if order.get('order_id')]

                if order_ids:
                    logger.info(f"🔄 Auto-syncing {len(order_ids)} pending orders...")

                    # Fetch status from GSM Fusion API
                    client = GSMFusionClient()
                    updated_orders = client.get_imei_orders(order_ids)
                    client.close()

                    # Update database with latest status
                    updated_count = 0
                    for api_order in updated_orders:
                        # Parse CODE field to extract individual fields
                        result_data = {}
                        cleaned_code = None

                        if api_order.code:
                            code_text = api_order.code

                            # Helper function to clean HTML tags
                            def clean_html(text):
                                # Remove HTML tags
                                text = re.sub(r'<[^>]+>', '', text)
                                # Remove <br> and &lt; &gt;
                                text = text.replace('<br>', '').replace('&lt;', '<').replace('&gt;', '>')
                                return text.strip()

                            # Clean the entire CODE field for display (multi-line format)
                            cleaned_code = code_text.replace('<br>', '\n').replace('&lt;br&gt;', '\n')
                            cleaned_code = re.sub(r'<[^>]+>', '', cleaned_code)  # Remove all HTML tags
                            cleaned_code = cleaned_code.replace('&lt;', '<').replace('&gt;', '>')
                            cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)  # Remove blank lines
                            cleaned_code = cleaned_code.strip()

                            # Extract fields from CODE
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

                            # Store ORIGINAL code for record keeping
                            result_data['result_code'] = api_order.code
                            # Store CLEANED code for display
                            result_data['result_code_display'] = cleaned_code

                        # Update order in database - pass both original and cleaned versions
                        db.update_order_status(
                            order_id=api_order.id,
                            status=api_order.status,
                            code=api_order.code,  # Original with HTML tags (record keeping)
                            code_display=cleaned_code,  # Cleaned for display
                            service_name=api_order.package,  # Service name from API
                            result_data=result_data if result_data else None
                        )
                        updated_count += 1

                    if updated_count > 0:
                        logger.info(f"✅ Auto-sync complete: Updated {updated_count} order(s)")

        except Exception as e:
            logger.error(f"❌ Auto-sync error: {str(e)}")

        # Wait for next sync interval
        time_module.sleep(AUTO_SYNC_INTERVAL)


if __name__ == '__main__':
    print("=" * 80)
    print("GSM FUSION WEB INTERFACE")
    print("=" * 80)
    print("\n✓ Starting web server...")
    print("✓ Server running at: http://localhost:5001")

    if AUTO_SYNC_ENABLED:
        print(f"✓ Auto-sync enabled (every {AUTO_SYNC_INTERVAL//60} minutes)")
        # Start background sync thread
        sync_thread = threading.Thread(target=auto_sync_orders, daemon=True)
        sync_thread.start()

    print("\nPress CTRL+C to stop the server\n")
    print("=" * 80)

    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
