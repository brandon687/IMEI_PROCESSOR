#!/usr/bin/env python3
"""
Test script to verify the manual sync parameter fix works correctly.
This will test the update_order_status method with the corrected parameters.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database module
from database import get_database

def test_update_order_status_signature():
    """Test that update_order_status accepts the correct parameters"""
    print("=" * 60)
    print("Testing update_order_status method signature")
    print("=" * 60)

    try:
        db = get_database()
        print(f"✓ Database connected (using {'Supabase' if db.use_supabase else 'SQLite'})")

        # Test parameters that will be passed from sync_and_parse_orders
        test_params = {
            'order_id': 'TEST12345',
            'status': 'Completed',
            'result_code': 'TEST_CODE',
            'result_code_display': 'Test Code Display',
            'result_data': {
                'carrier': 'Test Carrier',
                'model': 'Test Model',
                'simlock': 'Unlocked',
                'fmi': 'OFF',
                'imei2': '123456789012346',
                'serial_number': 'TESTSERIAL',
                'meid': '12345678901234',
                'gsma_status': 'Clean',
                'purchase_date': '2024-01-01',
                'applecare': 'Yes',
                'tether_policy': 'Test Policy'
            }
        }

        print("\nTest 1: Calling update_order_status with parsed data...")
        print(f"Parameters: {list(test_params.keys())}")

        # This should work now with the fixed parameters
        try:
            result = db.update_order_status(**test_params)
            print("✓ Method accepts parameters (call would execute if order exists)")
            print(f"  Return value: {result}")
        except TypeError as e:
            print(f"✗ Parameter error: {e}")
            return False

        print("\nTest 2: Calling update_order_status without result_data...")
        test_params_simple = {
            'order_id': 'TEST12345',
            'status': 'Completed',
            'result_code': 'TEST_CODE',
            'result_code_display': 'Test Code Display'
        }
        print(f"Parameters: {list(test_params_simple.keys())}")

        try:
            result = db.update_order_status(**test_params_simple)
            print("✓ Method accepts parameters (call would execute if order exists)")
            print(f"  Return value: {result}")
        except TypeError as e:
            print(f"✗ Parameter error: {e}")
            return False

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Parameters are correct!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_sync_function_parameters():
    """Verify the sync_and_parse_orders function uses correct parameters"""
    print("\n" + "=" * 60)
    print("Verifying sync_and_parse_orders parameter usage")
    print("=" * 60)

    import inspect
    from web_app import sync_and_parse_orders

    # Get the source code
    source = inspect.getsource(sync_and_parse_orders)

    # Check for old parameter names (should not exist)
    # We need to be careful to not match substrings of correct parameters
    import re

    # Match standalone 'code=' that's NOT 'result_code='
    has_standalone_code = re.search(r'(?<!result_)code=', source)
    # Match 'code_display=' that's NOT 'result_code_display='
    has_code_display = re.search(r'(?<!result_)code_display=', source)
    # Match 'service_name='
    has_service_name = 'service_name=' in source and 'update_order_status' in source

    found_old = []
    if has_standalone_code:
        found_old.append('code=')
    if has_code_display:
        found_old.append('code_display=')
    if has_service_name:
        found_old.append('service_name=')

    if found_old:
        print(f"✗ Found old parameter names: {found_old}")
        return False

    # Check for new parameter names (should exist)
    new_params = ['result_code=', 'result_code_display=']
    found_new = []
    for param in new_params:
        if param in source:
            found_new.append(param)

    if len(found_new) == len(new_params):
        print(f"✓ All correct parameter names found: {found_new}")
        print("✓ No old parameter names found")
        return True
    else:
        print(f"✗ Missing expected parameters. Found: {found_new}")
        return False

if __name__ == '__main__':
    print("\n🔧 Testing Manual Sync Parameter Fix\n")

    # Test 1: Database method signature
    test1_pass = test_update_order_status_signature()

    # Test 2: Verify web_app.py uses correct parameters
    test2_pass = verify_sync_function_parameters()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Database method signature test: {'✓ PASS' if test1_pass else '✗ FAIL'}")
    print(f"Web app parameter verification: {'✓ PASS' if test2_pass else '✗ FAIL'}")

    if test1_pass and test2_pass:
        print("\n✓✓✓ ALL TESTS PASSED - Ready to deploy! ✓✓✓")
        sys.exit(0)
    else:
        print("\n✗✗✗ TESTS FAILED - Do not deploy yet ✗✗✗")
        sys.exit(1)
