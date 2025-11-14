#!/usr/bin/env python3
"""Test order placement to see what error we get"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient

load_dotenv()

try:
    client = GSMFusionClient()

    print("Testing order placement...")
    print("IMEI: 353990097369512")
    print("Service ID: 1739")
    print()

    result = client.place_imei_order(
        imei="353990097369512",
        network_id="1739"
    )

    print("Result:")
    print(f"  Orders: {result['orders']}")
    print(f"  Duplicates: {result['duplicates']}")
    print(f"  Errors: {result['errors']}")

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
