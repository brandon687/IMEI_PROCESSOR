#!/usr/bin/env python3
"""Test with a fresh IMEI that hasn't been submitted"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient

load_dotenv()

try:
    client = GSMFusionClient()

    # Use a different IMEI that likely hasn't been submitted
    test_imei = "123456789012345"

    print("Testing order placement with fresh IMEI...")
    print(f"IMEI: {test_imei}")
    print("Service ID: 1739")
    print()

    result = client.place_imei_order(
        imei=test_imei,
        network_id="1739"
    )

    print("=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(f"Orders: {result['orders']}")
    print(f"Duplicates: {result['duplicates']}")
    print(f"Errors: {result['errors']}")
    print()

    if result['orders']:
        print(f"✅ SUCCESS! Order ID: {result['orders'][0]['id']}")
    elif result['errors']:
        print(f"❌ ERROR: {result['errors'][0]}")
    elif result['duplicates']:
        print(f"⚠️ DUPLICATE IMEI")

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
