#!/usr/bin/env python3
"""
Startup Validation Script
Ensures all requirements are met before starting the app
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Validate environment variables"""
    logger.info("Checking environment variables...")

    required = ['GSM_FUSION_API_KEY', 'GSM_FUSION_USERNAME']
    optional = ['SUPABASE_URL', 'SUPABASE_KEY']

    missing_required = []
    missing_optional = []

    for var in required:
        if not os.environ.get(var):
            missing_required.append(var)
        else:
            logger.info(f"  ✓ {var} is set")

    for var in optional:
        if not os.environ.get(var):
            missing_optional.append(var)
            logger.warning(f"  ⚠ {var} not set (optional)")
        else:
            logger.info(f"  ✓ {var} is set")

    if missing_required:
        logger.error(f"\n✗ Missing required environment variables: {', '.join(missing_required)}")
        return False

    if missing_optional:
        logger.warning(f"\n⚠ Missing optional variables: {', '.join(missing_optional)}")
        logger.warning("  App will run in degraded mode (no database)")

    return True

def check_imports():
    """Validate all imports work"""
    logger.info("\nChecking imports...")

    try:
        import flask
        logger.info("  ✓ Flask")
    except ImportError as e:
        logger.error(f"  ✗ Flask: {e}")
        return False

    try:
        import gunicorn
        logger.info("  ✓ Gunicorn")
    except ImportError as e:
        logger.error(f"  ✗ Gunicorn: {e}")
        return False

    try:
        from gsm_fusion_client import GSMFusionClient
        logger.info("  ✓ GSM Fusion Client")
    except ImportError as e:
        logger.error(f"  ✗ GSM Fusion Client: {e}")
        return False

    try:
        from database import get_database
        logger.info("  ✓ Database module")
    except ImportError as e:
        logger.error(f"  ✗ Database module: {e}")
        return False

    try:
        from supabase import create_client
        logger.info("  ✓ Supabase")
    except ImportError as e:
        logger.error(f"  ✗ Supabase: {e}")
        return False

    return True

def check_app():
    """Validate app can be imported"""
    logger.info("\nChecking application...")

    try:
        import web_app
        logger.info("  ✓ web_app module loaded")

        if hasattr(web_app, 'app'):
            logger.info("  ✓ Flask app instance exists")
        else:
            logger.error("  ✗ Flask app instance not found")
            return False

        if hasattr(web_app, 'get_services_cached'):
            logger.info("  ✓ Service caching function exists")
        else:
            logger.error("  ✗ Service caching function not found")
            return False

        return True
    except Exception as e:
        logger.error(f"  ✗ Failed to load web_app: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all validation checks"""
    logger.info("="*60)
    logger.info("STARTUP VALIDATION")
    logger.info("="*60)

    all_ok = True

    if not check_environment():
        all_ok = False

    if not check_imports():
        all_ok = False

    if not check_app():
        all_ok = False

    logger.info("\n" + "="*60)
    if all_ok:
        logger.info("✓✓✓ ALL CHECKS PASSED - READY TO START ✓✓✓")
        logger.info("="*60)
        return 0
    else:
        logger.error("✗✗✗ VALIDATION FAILED - FIX ERRORS BEFORE STARTING ✗✗✗")
        logger.info("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
