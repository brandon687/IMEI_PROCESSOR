#!/usr/bin/env python3
"""
Check if an IMEI can be submitted (won't be duplicate)
"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient
import sys

load_dotenv()

def check_imei(imei, service_id="1739"):
    """Check if IMEI can be submitted"""

    print("=" * 80)
    print("IMEI SUBMISSION CHECK")
    print("=" * 80)
    print(f"IMEI: {imei}")
    print(f"Service: {service_id}")
    print()

    try:
        client = GSMFusionClient()

        # Try to submit
        result = client.place_imei_order(imei=imei, network_id=service_id)

        client.close()

        if result['errors']:
            error = result['errors'][0]
            if 'already exists' in error.lower():
                print("❌ DUPLICATE - IMEI Already Submitted")
                print()
                print("This IMEI was previously submitted to Hammer Fusion.")
                print()
                print("📋 To view existing results:")
                print("   1. Go to: https://hammerfusion.com/imeiorders.php")
                print("   2. Press Ctrl+F (or Cmd+F on Mac)")
                print(f"   3. Search for: {imei}")
                print("   4. View the order results")
                print()
                print("💡 No need to resubmit - view original order instead!")
                return False
            else:
                print(f"❌ ERROR: {error}")
                return False

        elif result['orders']:
            order = result['orders'][0]
            print("✅ SUCCESS - Order Submitted!")
            print()
            print(f"Order ID: {order['id']}")
            print(f"Status: {order['status']}")
            print()
            print("View status with:")
            print(f"  python3 gsm_cli.py status {order['id']}")
            print()
            print("Or visit:")
            print(f"  http://localhost:5001/status/{order['id']}")
            return True

        elif result['duplicates']:
            print("❌ DUPLICATE - Already in System")
            print()
            print("Check order history at:")
            print("  https://hammerfusion.com/imeiorders.php")
            return False

        else:
            print("⚠️  Unknown response from API")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_if_submitted.py <IMEI> [service_id]")
        print()
        print("Examples:")
        print("  python3 check_if_submitted.py 353370080089458")
        print("  python3 check_if_submitted.py 123456789012345 1739")
        print()
        sys.exit(1)

    imei = sys.argv[1]
    service_id = sys.argv[2] if len(sys.argv) > 2 else "1739"

    check_imei(imei, service_id)
