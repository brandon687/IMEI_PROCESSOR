"""
Example 1: Simple IMEI Order Submission
========================================
This example shows the basic workflow for submitting an IMEI order
and checking its status.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError


def main():
    """Submit a simple IMEI order"""

    # Initialize client (reads credentials from environment variables)
    print("Initializing GSM Fusion client...")
    client = GSMFusionClient()

    try:
        # Step 1: List available services to find the right service ID
        print("\nStep 1: Fetching available services...")
        services = client.get_imei_services()

        print(f"\nFound {len(services)} services:")
        for i, service in enumerate(services[:5], 1):  # Show first 5
            print(f"{i}. {service.title} (ID: {service.package_id}) - ${service.price}")

        # Step 2: Submit IMEI order
        print("\n" + "="*80)
        print("Step 2: Submitting IMEI order...")

        # Replace these with your actual values
        imei = "123456789012345"
        network_id = "1"  # Use actual service ID from step 1

        print(f"IMEI: {imei}")
        print(f"Service ID: {network_id}")

        result = client.place_imei_order(
            imei=imei,
            network_id=network_id
        )

        # Check result
        if result['orders']:
            order = result['orders'][0]
            order_id = order['id']
            print(f"\n✓ Order submitted successfully!")
            print(f"Order ID: {order_id}")
            print(f"Status: {order['status']}")

            # Step 3: Check order status
            print("\n" + "="*80)
            print("Step 3: Checking order status...")

            orders = client.get_imei_orders(order_id)
            if orders:
                current_order = orders[0]
                print(f"\nOrder Status: {current_order.status}")
                print(f"IMEI: {current_order.imei}")
                print(f"Package: {current_order.package}")

                if current_order.code:
                    print(f"Code: {current_order.code}")
                else:
                    print("Code: Not yet available (order still processing)")

        elif result['duplicates']:
            print("\n⚠ This IMEI is already in the system (duplicate)")

    except GSMFusionAPIError as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

    finally:
        # Clean up
        client.close()
        print("\n" + "="*80)
        print("Done!")


if __name__ == "__main__":
    main()
