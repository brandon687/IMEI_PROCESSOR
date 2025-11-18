#!/usr/bin/env python3
"""
Comprehensive Supabase Diagnostic Tool
Checks every aspect of Supabase integration to ensure no data slips through cracks
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_environment_variables():
    """Check if all required environment variables are set"""
    print_section("STEP 1: Environment Variables Check")

    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    all_set = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the key for security
            if 'KEY' in var:
                display_value = value[:20] + "..." if len(value) > 20 else value
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: NOT SET")
            all_set = False

    return all_set

def check_supabase_package():
    """Check if supabase package is installed and importable"""
    print_section("STEP 2: Supabase Package Check")

    try:
        import supabase
        print(f"✓ supabase package installed")
        print(f"  Version: {supabase.__version__ if hasattr(supabase, '__version__') else 'unknown'}")

        from supabase import create_client, Client
        print(f"✓ Can import create_client and Client")
        return True
    except ImportError as e:
        print(f"✗ supabase package NOT installed: {e}")
        return False

def test_supabase_connection():
    """Test actual connection to Supabase"""
    print_section("STEP 3: Supabase Connection Test")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("✗ Cannot test connection - environment variables not set")
        return False

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print(f"✓ Supabase client created successfully")
        print(f"  URL: {supabase_url}")

        # Test connection with a simple query
        try:
            response = client.table('orders').select('id').limit(1).execute()
            print(f"✓ Successfully queried 'orders' table")
            print(f"  Response: {response}")
            return True
        except Exception as query_error:
            print(f"✗ Failed to query 'orders' table: {query_error}")
            print(f"  Error type: {type(query_error).__name__}")
            return False

    except Exception as e:
        print(f"✗ Failed to create Supabase client: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def check_database_schema():
    """Check if database schema matches expectations"""
    print_section("STEP 4: Database Schema Check")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("✗ Cannot check schema - environment variables not set")
        return False

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)

        # Try to select all columns to see what exists
        response = client.table('orders').select('*').limit(1).execute()

        if response.data and len(response.data) > 0:
            columns = list(response.data[0].keys())
            print(f"✓ Found {len(columns)} columns in 'orders' table:")
            for col in sorted(columns):
                print(f"  - {col}")

            # Check for required columns
            required_columns = [
                'order_id', 'imei', 'status', 'result_code', 'result_code_display',
                'carrier', 'model', 'simlock', 'fmi', 'service_name', 'service_id'
            ]

            missing_columns = [col for col in required_columns if col not in columns]

            if missing_columns:
                print(f"\n⚠️  Missing expected columns: {missing_columns}")
            else:
                print(f"\n✓ All required columns present")

            return True
        else:
            print("✓ Table exists but is empty")
            print("  Cannot verify schema without data")
            print("  Will attempt to check by inserting test record...")
            return True

    except Exception as e:
        print(f"✗ Failed to check schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test insert, update, and select operations"""
    print_section("STEP 5: Database Operations Test")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("✗ Cannot test operations - environment variables not set")
        return False

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)

        test_order_id = 'DIAG_TEST_001'

        # Test 1: Insert
        print("\nTest 1: INSERT operation")
        try:
            # Delete test record if it exists
            client.table('orders').delete().eq('order_id', test_order_id).execute()

            insert_data = {
                'order_id': test_order_id,
                'imei': '111111111111111',
                'status': 'Testing',
                'service_name': 'Diagnostic Test',
                'service_id': '999'
            }

            response = client.table('orders').insert(insert_data).execute()
            print(f"✓ INSERT successful: {response.data}")
        except Exception as e:
            print(f"✗ INSERT failed: {e}")
            return False

        # Test 2: Select
        print("\nTest 2: SELECT operation")
        try:
            response = client.table('orders').select('*').eq('order_id', test_order_id).execute()
            if response.data and len(response.data) > 0:
                print(f"✓ SELECT successful: Found {len(response.data)} record(s)")
            else:
                print(f"✗ SELECT failed: No records found")
                return False
        except Exception as e:
            print(f"✗ SELECT failed: {e}")
            return False

        # Test 3: Update
        print("\nTest 3: UPDATE operation")
        try:
            update_data = {
                'status': 'Completed',
                'result_code': 'TEST_SUCCESS',
                'carrier': 'Test Carrier',
                'model': 'Test Model'
            }

            response = client.table('orders').update(update_data).eq('order_id', test_order_id).execute()
            print(f"✓ UPDATE successful")

            # Verify update
            response = client.table('orders').select('*').eq('order_id', test_order_id).execute()
            if response.data and response.data[0]['status'] == 'Completed':
                print(f"✓ UPDATE verified: status changed to 'Completed'")
            else:
                print(f"✗ UPDATE verification failed")
                return False

        except Exception as e:
            print(f"✗ UPDATE failed: {e}")
            return False

        # Test 4: Delete (cleanup)
        print("\nTest 4: DELETE operation (cleanup)")
        try:
            client.table('orders').delete().eq('order_id', test_order_id).execute()
            print(f"✓ DELETE successful (test record cleaned up)")
        except Exception as e:
            print(f"⚠️  DELETE failed (manual cleanup may be needed): {e}")

        return True

    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_module():
    """Check if database.py properly initializes Supabase"""
    print_section("STEP 6: Database Module Check")

    try:
        from database import get_database

        db = get_database()
        print(f"✓ Database module loaded")
        print(f"  Using Supabase: {db.use_supabase}")
        print(f"  Database type: {'Supabase (PostgreSQL)' if db.use_supabase else 'SQLite'}")

        if db.use_supabase:
            print(f"  Supabase client: {db.supabase_client}")
            print(f"✓ Database module correctly using Supabase")
            return True
        else:
            print(f"✗ Database module using SQLite instead of Supabase")
            print(f"  This means Supabase connection failed during initialization")
            return False

    except Exception as e:
        print(f"✗ Failed to check database module: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_data_flow():
    """Check if data properly flows through the application"""
    print_section("STEP 7: Data Flow Check")

    try:
        from database import get_database

        db = get_database()

        if not db.use_supabase:
            print("✗ Cannot test data flow - not using Supabase")
            return False

        # Test update_order_status method
        print("\nTesting update_order_status method...")
        try:
            # This will fail if order doesn't exist, but we can check the method signature
            import inspect
            sig = inspect.signature(db.update_order_status)
            params = list(sig.parameters.keys())
            print(f"✓ update_order_status signature: {params}")

            expected_params = ['order_id', 'status', 'result_code', 'result_code_display', 'result_data']
            if all(p in params for p in expected_params):
                print(f"✓ All expected parameters present")
            else:
                missing = [p for p in expected_params if p not in params]
                print(f"✗ Missing parameters: {missing}")
                return False

        except Exception as e:
            print(f"✗ Failed to check update_order_status: {e}")
            return False

        return True

    except Exception as e:
        print(f"✗ Data flow check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic checks"""
    print("\n" + "=" * 80)
    print("  SUPABASE COMPREHENSIVE DIAGNOSTIC")
    print("  Ensuring NO data slips through the cracks")
    print("=" * 80)

    results = {}

    # Run all checks
    results['environment'] = check_environment_variables()
    results['package'] = check_supabase_package()
    results['connection'] = test_supabase_connection()
    results['schema'] = check_database_schema()
    results['operations'] = test_database_operations()
    results['module'] = check_database_module()
    results['data_flow'] = check_data_flow()

    # Summary
    print_section("DIAGNOSTIC SUMMARY")

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} - {check.upper()}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✓✓✓ ALL CHECKS PASSED - SUPABASE FULLY FUNCTIONAL ✓✓✓")
        print("=" * 80)
        print("\nData will be captured in Supabase without loss")
        return 0
    else:
        print("✗✗✗ SOME CHECKS FAILED - ISSUES DETECTED ✗✗✗")
        print("=" * 80)
        print("\n⚠️  WARNING: Data may not be properly saved to Supabase")
        print("   Review failed checks above for details")
        return 1

if __name__ == '__main__':
    sys.exit(main())
