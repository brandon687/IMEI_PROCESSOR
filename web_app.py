#!/usr/bin/env python3
"""
GSM Fusion Web Interface - PRODUCTION HARDENED
Zero-downtime version with comprehensive error handling
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError
from database import get_database
from production_submission_system import ProductionSubmissionSystem, SubmissionResult
import os
import logging
import traceback
from functools import wraps
import time
import csv
import io
import openpyxl
from datetime import datetime
import threading
import re

# Setup logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global state
_db_instance = None
_services_cache = None
_services_cache_time = 0
CACHE_DURATION = 300  # 5 minutes


def get_db_safe():
    """Get database with error handling - never crashes"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = get_database()
            logger.info("✓ Database connected successfully")
            return _db_instance
        except ValueError as e:
            logger.error(f"Database config error: {e}")
            return None
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    return _db_instance


def get_services_cached(max_age=300):
    """Get services with caching and error handling"""
    global _services_cache, _services_cache_time

    now = time.time()
    if _services_cache and (now - _services_cache_time < max_age):
        logger.info(f"Using cached services ({len(_services_cache)} items)")
        return _services_cache

    try:
        logger.info("Fetching fresh services from API...")
        client = GSMFusionClient(timeout=10)  # 10 second timeout
        services = client.get_imei_services()
        client.close()

        _services_cache = services
        _services_cache_time = now
        logger.info(f"✓ Fetched {len(services)} services successfully")
        return services

    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        logger.error(traceback.format_exc())

        # Return cached data even if stale
        if _services_cache:
            logger.warning(f"Returning stale cache ({len(_services_cache)} items)")
            return _services_cache

        # Return empty list as last resort
        return []


def error_handler(f):
    """Decorator to catch all errors and return error page"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GSMFusionAPIError as e:
            logger.error(f"API Error in {f.__name__}: {e}")
            return render_template('error.html', error=f"API Error: {str(e)}"), 500
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}")
            logger.error(traceback.format_exc())
            return render_template('error.html', error=f"Application Error: {str(e)}"), 500
    return wrapper


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring (simple)"""
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }

    # Check database
    try:
        db = get_db_safe()
        if db:
            health_status['checks']['database'] = 'connected'
        else:
            health_status['checks']['database'] = 'not_configured'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'

    # Check API (with cache)
    try:
        services = get_services_cached(max_age=60)
        health_status['checks']['api'] = f'ok ({len(services)} services)'
    except Exception as e:
        health_status['checks']['api'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@app.route('/api/debug')
def api_debug():
    """Deep diagnostic endpoint - shows EXACT API response"""
    if not os.environ.get('ENABLE_DEBUG_ENDPOINT'):
        return jsonify({'error': 'Debug endpoint disabled. Set ENABLE_DEBUG_ENDPOINT=1 to enable'}), 403

    diagnostic = {
        'timestamp': time.time(),
        'environment': {
            'API_KEY_SET': bool(os.environ.get('GSM_FUSION_API_KEY')),
            'API_KEY_LENGTH': len(os.environ.get('GSM_FUSION_API_KEY', '')),
            'USERNAME': os.environ.get('GSM_FUSION_USERNAME', 'NOT_SET'),
            'BASE_URL': os.environ.get('GSM_FUSION_BASE_URL', 'http://hammerfusion.com'),
        },
        'api_test': {}
    }

    try:
        logger.info("=== DIAGNOSTIC API TEST STARTING ===")
        client = GSMFusionClient(timeout=10)

        # Make raw request
        xml_response = client._make_request('imeiservices')

        diagnostic['api_test'] = {
            'success': True,
            'raw_xml_length': len(xml_response),
            'raw_xml_first_500': xml_response[:500],
            'raw_xml_last_500': xml_response[-500:] if len(xml_response) > 500 else xml_response,
            'full_xml': xml_response  # FULL response for analysis
        }

        # Try parsing
        try:
            parsed = client._parse_xml_response(xml_response)
            diagnostic['api_test']['parsed_successfully'] = True
            diagnostic['api_test']['parsed_type'] = str(type(parsed))
            diagnostic['api_test']['parsed_keys'] = list(parsed.keys()) if isinstance(parsed, dict) else 'NOT A DICT'
            diagnostic['api_test']['parsed_data'] = str(parsed)[:1000]  # First 1000 chars
        except Exception as parse_error:
            diagnostic['api_test']['parsed_successfully'] = False
            diagnostic['api_test']['parse_error'] = str(parse_error)

        client.close()

    except Exception as e:
        diagnostic['api_test'] = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

    return jsonify(diagnostic)


@app.route('/api/status')
def api_status():
    """Real-time API status for status bar - lightweight and fast"""
    status = {
        'timestamp': time.time(),
        'services': {
            'gsm_fusion': {'status': 'unknown', 'message': '', 'response_time': None},
            'database': {'status': 'unknown', 'message': ''},
            'cache': {'status': 'unknown', 'message': ''}
        },
        'overall': 'checking'
    }

    # Check GSM Fusion API
    try:
        start = time.time()
        client = GSMFusionClient(timeout=5)
        # Quick test - just check if we can create client
        client.close()
        response_time = round((time.time() - start) * 1000, 2)  # ms

        # Check if we have services cached
        services = get_services_cached(max_age=300)
        service_count = len(services)

        if service_count > 0:
            status['services']['gsm_fusion'] = {
                'status': 'operational',
                'message': f'{service_count} services available',
                'response_time': response_time
            }
        else:
            status['services']['gsm_fusion'] = {
                'status': 'degraded',
                'message': 'API responding but 0 services returned',
                'response_time': response_time
            }
    except Exception as e:
        status['services']['gsm_fusion'] = {
            'status': 'outage',
            'message': f'API Error: {str(e)[:100]}',
            'response_time': None
        }

    # Check Database
    try:
        db = get_db_safe()
        if db:
            status['services']['database'] = {
                'status': 'operational',
                'message': 'Supabase connected'
            }
        else:
            status['services']['database'] = {
                'status': 'not_configured',
                'message': 'Database not configured'
            }
    except Exception as e:
        status['services']['database'] = {
            'status': 'outage',
            'message': f'DB Error: {str(e)[:100]}'
        }

    # Check Cache
    if _services_cache:
        cache_age = int(time.time() - _services_cache_time)
        status['services']['cache'] = {
            'status': 'operational',
            'message': f'{len(_services_cache)} services (age: {cache_age}s)'
        }
    else:
        status['services']['cache'] = {
            'status': 'empty',
            'message': 'No cached data'
        }

    # Determine overall status
    statuses = [s['status'] for s in status['services'].values()]
    if 'outage' in statuses:
        status['overall'] = 'outage'
    elif 'degraded' in statuses:
        status['overall'] = 'degraded'
    elif all(s in ['operational', 'not_configured'] for s in statuses):
        status['overall'] = 'operational'
    else:
        status['overall'] = 'unknown'

    return jsonify(status)


@app.route('/')
@error_handler
def index():
    """Home page - bulletproof version"""
    logger.info("INDEX route called")

    # Check database (non-blocking)
    db = get_db_safe()
    if db is None:
        logger.warning("Database not available, continuing without it")

    # Get services with caching and error handling
    services = get_services_cached()

    if not services:
        logger.warning("No services available")
        return render_template('error.html',
                             error="Unable to load services. Please try again later."), 503

    # Get popular services (first 20)
    popular_services = services[:20] if len(services) > 20 else services

    logger.info(f"✓ Rendering index with {len(popular_services)} services")

    return render_template('index.html',
                         services=popular_services,
                         total_services=len(services),
                         recent_orders=[])


@app.route('/services')
@error_handler
def services_page():
    """Full services list page"""
    logger.info("SERVICES route called")

    services = get_services_cached()

    if not services:
        return render_template('error.html',
                             error="Unable to load services. Please try again later."), 503

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


# ==========================================
# SUBMISSION ROUTES
# ==========================================

@app.route('/submit', methods=['GET', 'POST'])
@error_handler
def submit():
    """Submit single or multiple IMEI orders"""
    logger.info("SUBMIT route called")

    if request.method == 'POST':
        imei_input = request.form.get('imei', '').strip()
        service_id = request.form.get('service_id', '').strip()
        force_recheck = request.form.get('force_recheck') == 'true'

        if not imei_input or not service_id:
            flash('IMEI and Service ID are required', 'error')
            return redirect(url_for('submit'))

        # Parse multiple IMEIs (one per line)
        imei_lines = imei_input.strip().split('\n')
        imeis = []
        for line in imei_lines:
            imei = line.strip()
            if imei:
                # Validate IMEI (15 digits)
                if not imei.isdigit() or len(imei) != 15:
                    flash(f'Invalid IMEI: {imei}. Must be 15 digits. Skipped.', 'warning')
                    continue
                imeis.append(imei)

        if not imeis:
            flash('No valid IMEIs found. Each IMEI must be 15 digits.', 'error')
            return redirect(url_for('submit'))

        # Submit orders using GSM Fusion client
        try:
            client = GSMFusionClient(timeout=30)
            result = client.place_imei_order(imeis, service_id, force_recheck=force_recheck)
            client.close()

            # Store in database
            db = get_db_safe()
            if db and result['orders']:
                for order in result['orders']:
                    try:
                        db.insert_order({
                            'order_id': order['id'],
                            'imei': order['imei'],
                            'service_id': service_id,
                            'status': order.get('status', 'Pending')
                        })
                    except Exception as e:
                        logger.warning(f"DB insert failed: {e}")

            # Show summary
            successful = len(result['orders'])
            duplicates = len(result['duplicates'])
            errors = len(result['errors'])

            if successful > 0:
                flash(f'✅ Submitted {successful} order(s) successfully!', 'success')
                if duplicates > 0:
                    flash(f'⚠️ {duplicates} duplicate(s) skipped', 'warning')
                if errors > 0:
                    flash(f'❌ {errors} error(s) occurred', 'error')
                return redirect(url_for('history'))
            else:
                if duplicates > 0:
                    flash(f'All IMEIs are duplicates ({duplicates} total)', 'warning')
                if errors > 0:
                    flash(f'Submission failed: {errors} error(s)', 'error')
                    for error in result['errors'][:3]:  # Show first 3 errors
                        flash(f'Error: {error}', 'error')
                return redirect(url_for('submit'))

        except Exception as e:
            logger.error(f"Submission error: {e}")
            logger.error(traceback.format_exc())
            flash(f'Submission failed: {str(e)}', 'error')
            return redirect(url_for('submit'))

    # GET request - show form
    services = get_services_cached()
    if not services:
        return render_template('error.html', error="Unable to load services"), 503

    return render_template('submit.html', services=services)


@app.route('/batch', methods=['GET', 'POST'])
@error_handler
def batch_upload():
    """Batch CSV/Excel upload"""
    logger.info("BATCH route called")

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('batch_upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('batch_upload'))

        service_id = request.form.get('service_id', '').strip()
        if not service_id:
            flash('Service ID is required', 'error')
            return redirect(url_for('batch_upload'))

        try:
            # Parse file based on extension
            if file.filename.endswith('.csv'):
                # Read CSV
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.DictReader(stream)
                imeis = [row.get('imei', '').strip() for row in csv_reader if row.get('imei')]
            elif file.filename.endswith(('.xlsx', '.xls')):
                # Read Excel
                wb = openpyxl.load_workbook(file)
                ws = wb.active
                headers = [cell.value for cell in ws[1]]
                imei_col = headers.index('imei') if 'imei' in headers else 0
                imeis = [str(ws.cell(row, imei_col + 1).value).strip()
                        for row in range(2, ws.max_row + 1)
                        if ws.cell(row, imei_col + 1).value]
            else:
                flash('Invalid file format. Use CSV or Excel.', 'error')
                return redirect(url_for('batch_upload'))

            # Validate IMEIs
            valid_imeis = [imei for imei in imeis if imei.isdigit() and len(imei) == 15]

            if not valid_imeis:
                flash('No valid IMEIs found in file', 'error')
                return redirect(url_for('batch_upload'))

            flash(f'Processing {len(valid_imeis)} IMEIs from file...', 'info')

            # Submit batch
            client = GSMFusionClient(timeout=30)
            result = client.place_imei_order(valid_imeis, service_id)
            client.close()

            # Store in database
            db = get_db_safe()
            if db and result['orders']:
                for order in result['orders']:
                    try:
                        db.insert_order({
                            'order_id': order['id'],
                            'imei': order['imei'],
                            'service_id': service_id,
                            'status': order.get('status', 'Pending')
                        })
                    except Exception as e:
                        logger.warning(f"DB insert failed: {e}")

            successful = len(result['orders'])
            duplicates = len(result['duplicates'])
            errors = len(result['errors'])

            flash(f'Batch processed: {successful} successful, {duplicates} duplicates, {errors} errors', 'success')
            return redirect(url_for('history'))

        except Exception as e:
            logger.error(f"Batch upload error: {e}")
            logger.error(traceback.format_exc())
            flash(f'Batch upload failed: {str(e)}', 'error')
            return redirect(url_for('batch_upload'))

    # GET - show form
    services = get_services_cached()
    return render_template('batch.html', services=services)


# ==========================================
# HISTORY & ORDER ROUTES
# ==========================================

@app.route('/history')
@error_handler
def history():
    """View order history"""
    logger.info("HISTORY route called")

    search_imei = request.args.get('imei', '').strip()

    db = get_db_safe()
    if not db:
        flash('Database not available', 'warning')
        return render_template('history.html', orders=[], search_query='')

    try:
        if search_imei:
            # Parse multiple IMEIs
            imeis = [line.strip() for line in search_imei.split('\n')
                    if line.strip() and line.strip().isdigit() and len(line.strip()) == 15]

            if len(imeis) == 1:
                orders = db.search_orders_by_imei(imeis[0])
            elif len(imeis) > 1:
                # Search multiple IMEIs
                all_orders = []
                for imei in imeis:
                    all_orders.extend(db.search_orders_by_imei(imei))
                orders = all_orders
            else:
                orders = []
                flash('No valid IMEIs found', 'warning')
        else:
            orders = db.get_recent_orders(limit=100)

        return render_template('history.html',
                             orders=orders,
                             search_query=search_imei)

    except Exception as e:
        logger.error(f"History error: {e}")
        logger.error(traceback.format_exc())
        flash(f'Error loading history: {str(e)}', 'error')
        return render_template('history.html', orders=[], search_query='')


@app.route('/status/<order_id>')
@error_handler
def order_status(order_id):
    """Check order status"""
    logger.info(f"STATUS route called for order: {order_id}")

    db = get_db_safe()

    # Try database first
    if db:
        try:
            # Search by order_id or IMEI
            conn = db.conn
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ? OR imei = ? LIMIT 1", (order_id, order_id))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                order = dict(zip(columns, row))
                return render_template('status.html', order=order)
        except Exception as e:
            logger.warning(f"DB lookup failed: {e}")

    # Fallback to API
    try:
        client = GSMFusionClient(timeout=10)
        orders = client.get_imei_orders(order_id)
        client.close()

        if not orders:
            flash('Order not found', 'error')
            return redirect(url_for('index'))

        # Convert IMEIOrder to dict for template
        order = {
            'order_id': orders[0].id,
            'imei': orders[0].imei,
            'service_name': orders[0].package,
            'status': orders[0].status,
            'code': orders[0].code,
            'order_date': orders[0].requested_at
        }

        return render_template('status.html', order=order)
    except Exception as e:
        logger.error(f"Order status error: {e}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error=f"Unable to fetch order status: {str(e)}")


# ==========================================
# SERVICE & DATABASE ROUTES
# ==========================================

@app.route('/service/<service_id>')
@error_handler
def service_detail(service_id):
    """View service details"""
    logger.info(f"SERVICE DETAIL route called for: {service_id}")

    services = get_services_cached()

    # Find service
    service = next((s for s in services if s.package_id == service_id), None)

    if not service:
        flash('Service not found', 'error')
        return redirect(url_for('services_page'))

    return render_template('service_detail.html', service=service)


@app.route('/database')
@error_handler
def database_view():
    """View database statistics"""
    logger.info("DATABASE route called")

    db = get_db_safe()
    if not db:
        flash('Database not available', 'error')
        return redirect(url_for('index'))

    try:
        # Get recent orders
        orders = db.get_recent_orders(limit=50)

        # Calculate simple stats
        total_orders = len(orders)
        completed = len([o for o in orders if o.get('status', '').lower() == 'completed'])
        pending = len([o for o in orders if o.get('status', '').lower() in ['pending', 'in process']])

        stats = {
            'total_orders': total_orders,
            'completed': completed,
            'pending': pending
        }

        return render_template('database.html',
                             stats=stats,
                             orders=orders)
    except Exception as e:
        logger.error(f"Database view error: {e}")
        logger.error(traceback.format_exc())
        flash(f'Database error: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {e}")
    return render_template('error.html', error="Internal server error"), 500


@app.before_request
def before_request():
    """Log all requests for debugging"""
    logger.info(f"Request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log all responses"""
    logger.info(f"Response: {response.status_code} for {request.path}")
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))

    # Pre-warm cache on startup
    logger.info("Starting application...")
    logger.info("Pre-warming services cache...")
    try:
        services = get_services_cached()
        logger.info(f"✓ Cache warmed with {len(services)} services")
    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")
        logger.warning("Continuing anyway - cache will populate on first request")

    logger.info(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
