#!/usr/bin/env python3
"""
GSM Fusion Web Interface - PRODUCTION HARDENED
Zero-downtime version with comprehensive error handling
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError
from database import get_database
import os
import logging
import traceback
from functools import wraps
import time

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
