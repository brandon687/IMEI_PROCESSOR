#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION READINESS TEST SUITE
Tests all critical paths and error conditions
"""

import sys
import time
import logging
from typing import Dict, List
import traceback

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name):
        self.passed += 1
        logger.info(f"✓ PASS: {test_name}")

    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        logger.error(f"✗ FAIL: {test_name}")
        logger.error(f"  Error: {error}")

    def summary(self):
        total = self.passed + self.failed
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        logger.info(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")

        if self.failed > 0:
            logger.info("\n" + "="*60)
            logger.info("FAILED TESTS:")
            logger.info("="*60)
            for test_name, error in self.errors:
                logger.info(f"\n{test_name}:")
                logger.info(f"  {error}")

        return self.failed == 0


def test_imports(results: TestResult):
    """Test 1: All critical imports work"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 1: IMPORTS")
    logger.info("="*60)

    try:
        import flask
        results.add_pass("Import Flask")
    except Exception as e:
        results.add_fail("Import Flask", str(e))

    try:
        from gsm_fusion_client import GSMFusionClient
        results.add_pass("Import GSMFusionClient")
    except Exception as e:
        results.add_fail("Import GSMFusionClient", str(e))

    try:
        from database import get_database, IMEIDatabase
        results.add_pass("Import Database modules")
    except Exception as e:
        results.add_fail("Import Database modules", str(e))

    try:
        from supabase import create_client
        results.add_pass("Import Supabase")
    except Exception as e:
        results.add_fail("Import Supabase", str(e))


def test_database_module(results: TestResult):
    """Test 2: Database module structure"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 2: DATABASE MODULE")
    logger.info("="*60)

    try:
        from database import IMEIDatabase, get_database

        # Test that IMEIDatabase has required methods
        required_methods = [
            'insert_order', 'update_order_status', 'get_order_by_id',
            'get_orders_by_imei', 'get_recent_orders', 'search_orders'
        ]

        for method in required_methods:
            if hasattr(IMEIDatabase, method):
                results.add_pass(f"Database has {method} method")
            else:
                results.add_fail(f"Database has {method} method", "Method not found")

    except Exception as e:
        results.add_fail("Database module structure", str(e))


def test_gsm_client_structure(results: TestResult):
    """Test 3: GSM Fusion client structure"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 3: GSM FUSION CLIENT")
    logger.info("="*60)

    try:
        from gsm_fusion_client import GSMFusionClient, ServiceInfo

        # Test ServiceInfo dataclass
        if hasattr(ServiceInfo, 'package_id'):
            results.add_pass("ServiceInfo has package_id field")
        else:
            results.add_fail("ServiceInfo has package_id field", "Field not found")

        # Test GSMFusionClient methods
        required_methods = ['get_imei_services', 'place_imei_order', 'get_imei_orders', 'close']
        for method in required_methods:
            if hasattr(GSMFusionClient, method):
                results.add_pass(f"GSMFusionClient has {method} method")
            else:
                results.add_fail(f"GSMFusionClient has {method} method", "Method not found")

    except Exception as e:
        results.add_fail("GSM client structure", str(e))


def test_xml_parsing(results: TestResult):
    """Test 4: XML parsing robustness"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 4: XML PARSING")
    logger.info("="*60)

    try:
        import xml.etree.ElementTree as ET
        from gsm_fusion_client import GSMFusionClient

        # Create dummy client to access parsing method
        test_xml = '''<?xml version="1.0"?>
<Response>
    <Package>
        <PackageId>1</PackageId>
        <PackageTitle>Test Service</PackageTitle>
        <PackagePrice>0.10</PackagePrice>
    </Package>
</Response>'''

        root = ET.fromstring(test_xml)

        # Test that it doesn't crash
        results.add_pass("XML parsing doesn't crash")

        # Test that Package elements are dicts
        from gsm_fusion_client import GSMFusionClient
        import os

        # Mock environment for testing
        os.environ.setdefault('GSM_FUSION_API_KEY', 'test-key')
        os.environ.setdefault('GSM_FUSION_USERNAME', 'test-user')

        try:
            client = GSMFusionClient()
            parsed = client._xml_to_dict(root)

            if 'Package' in parsed:
                pkg = parsed['Package']
                if isinstance(pkg, dict):
                    results.add_pass("Package is dict (not string)")

                    if 'PackageId' in pkg:
                        results.add_pass("Package has PackageId field")
                    else:
                        results.add_fail("Package has PackageId field", "Field not found")
                else:
                    results.add_fail("Package is dict (not string)", f"Got {type(pkg)}")
            else:
                results.add_fail("Package element exists", "Package not in parsed result")

            client.close()
        except Exception as e:
            results.add_fail("XML to dict conversion", str(e))

    except Exception as e:
        results.add_fail("XML parsing test", str(e))


def test_error_handling(results: TestResult):
    """Test 5: Error handling"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 5: ERROR HANDLING")
    logger.info("="*60)

    try:
        from gsm_fusion_client import GSMFusionAPIError

        # Test that custom exception exists
        results.add_pass("GSMFusionAPIError exception exists")

        # Test that it can be raised and caught
        try:
            raise GSMFusionAPIError("Test error")
        except GSMFusionAPIError as e:
            if str(e) == "Test error":
                results.add_pass("GSMFusionAPIError can be raised and caught")
            else:
                results.add_fail("GSMFusionAPIError message", f"Got: {str(e)}")

    except Exception as e:
        results.add_fail("Error handling test", str(e))


def test_web_app_structure(results: TestResult):
    """Test 6: Web app structure"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 6: WEB APPLICATION")
    logger.info("="*60)

    try:
        import web_app_v2
        from flask import Flask

        # Test that app is Flask instance
        if isinstance(web_app_v2.app, Flask):
            results.add_pass("app is Flask instance")
        else:
            results.add_fail("app is Flask instance", f"Got {type(web_app_v2.app)}")

        # Test required routes exist
        routes = [rule.rule for rule in web_app_v2.app.url_map.iter_rules()]

        required_routes = ['/', '/health', '/services']
        for route in required_routes:
            if route in routes:
                results.add_pass(f"Route {route} exists")
            else:
                results.add_fail(f"Route {route} exists", "Route not found")

        # Test helper functions exist
        if hasattr(web_app_v2, 'get_db_safe'):
            results.add_pass("get_db_safe function exists")
        else:
            results.add_fail("get_db_safe function exists", "Function not found")

        if hasattr(web_app_v2, 'get_services_cached'):
            results.add_pass("get_services_cached function exists")
        else:
            results.add_fail("get_services_cached function exists", "Function not found")

    except Exception as e:
        results.add_fail("Web app structure test", str(e))
        logger.error(traceback.format_exc())


def test_environment_variables(results: TestResult):
    """Test 7: Environment variable handling"""
    logger.info("\n" + "="*60)
    logger.info("TEST SUITE 7: ENVIRONMENT VARIABLES")
    logger.info("="*60)

    import os

    # Test that critical env vars are checked (not just assumed)
    try:
        from database import IMEIDatabase

        # Test with missing env vars
        old_url = os.environ.get('SUPABASE_URL')
        old_key = os.environ.get('SUPABASE_KEY')

        if 'SUPABASE_URL' in os.environ:
            del os.environ['SUPABASE_URL']
        if 'SUPABASE_KEY' in os.environ:
            del os.environ['SUPABASE_KEY']

        try:
            db = IMEIDatabase()
            results.add_fail("Database raises error on missing credentials", "No error raised")
        except ValueError as e:
            if 'SUPABASE' in str(e):
                results.add_pass("Database raises ValueError on missing credentials")
            else:
                results.add_fail("Database error message mentions Supabase", str(e))
        except Exception as e:
            results.add_fail("Database raises correct error type", f"Got {type(e)}: {e}")
        finally:
            # Restore env vars
            if old_url:
                os.environ['SUPABASE_URL'] = old_url
            if old_key:
                os.environ['SUPABASE_KEY'] = old_key

    except Exception as e:
        results.add_fail("Environment variable handling", str(e))


def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("PRODUCTION READINESS TEST SUITE")
    logger.info("="*60)
    logger.info("Testing HAMMER-API for production deployment")
    logger.info(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = TestResult()

    # Run all test suites
    test_imports(results)
    test_database_module(results)
    test_gsm_client_structure(results)
    test_xml_parsing(results)
    test_error_handling(results)
    test_web_app_structure(results)
    test_environment_variables(results)

    # Print summary
    all_passed = results.summary()

    logger.info(f"\nCompleted at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)

    if all_passed:
        logger.info("✓✓✓ ALL TESTS PASSED - READY FOR PRODUCTION ✓✓✓")
        return 0
    else:
        logger.error("✗✗✗ SOME TESTS FAILED - NOT READY FOR PRODUCTION ✗✗✗")
        return 1


if __name__ == '__main__':
    sys.exit(main())
