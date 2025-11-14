#!/usr/bin/env python3
"""
Complete Order Flow Demo
Shows the full process of submitting and tracking an order
"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient
import time

load_dotenv()

def demo_order_flow():
    """Demonstrate the complete order flow"""

    print("=" * 80)
    print("GSM FUSION ORDER FLOW DEMO")
    print("=" * 80)

    # Initialize client
    client = GSMFusionClient()

    # STEP 1: Browse available services
    print("\n[STEP 1] Fetching available services...")
    services = client.get_imei_services()

    print(f"\nFound {len(services)} services. Here are the first 5:")
    print("-" * 80)
    for i, service in enumerate(services[:5], 1):
        print(f"{i}. ID: {service.package_id}")
        print(f"   Name: {service.title}")
        print(f"   Price: ${service.price}")
        print(f"   Delivery: {service.delivery_time}")
        print(f"   Category: {service.category}")
        print()

    # STEP 2: Submit an order (example - won't actually submit)
    print("\n[STEP 2] Submitting an order...")
    print("-" * 80)
    print("Example command:")
    print("  python3 gsm_cli.py submit 123456789012345 1739")
    print("\nThis would:")
    print("  - Submit IMEI: 123456789012345")
    print("  - Using Service ID: 1739")
    print("  - Return an Order ID (e.g., 12345)")

    # Uncomment below to actually submit (replace with real IMEI)
    """
    result = client.place_imei_order(
        imei="YOUR_REAL_IMEI_HERE",
        network_id="1739"
    )

    if result['orders']:
        order_id = result['orders'][0]['id']
        print(f"\n✓ Order submitted! Order ID: {order_id}")
    """

    # STEP 3: Check order status (example)
    print("\n[STEP 3] Checking order status...")
    print("-" * 80)
    print("Example command:")
    print("  python3 gsm_cli.py status 12345")
    print("\nThis would return:")
    print("  - Order ID: 12345")
    print("  - IMEI: 123456789012345")
    print("  - Status: Pending/In Process/Completed")
    print("  - Code: [Result data when completed]")

    # Uncomment below to check a real order
    """
    orders = client.get_imei_orders("YOUR_ORDER_ID_HERE")
    for order in orders:
        print(f"\nOrder ID: {order.id}")
        print(f"IMEI: {order.imei}")
        print(f"Status: {order.status}")
        print(f"Package: {order.package}")
        if order.code:
            print(f"Result: {order.code}")
    """

    # STEP 4: Wait for completion (optional)
    print("\n[STEP 4] Wait for order completion (optional)...")
    print("-" * 80)
    print("Example command:")
    print("  python3 gsm_cli.py wait 12345")
    print("\nThis will:")
    print("  - Check order status every 60 seconds")
    print("  - Automatically notify when completed")
    print("  - Display the final result")

    # STEP 5: Extract results
    print("\n[STEP 5] Extracting results...")
    print("-" * 80)
    print("Once completed, the 'Code' field contains your results:")
    print("  - For checker services: Full device details")
    print("  - For unlock services: Unlock code or confirmation")
    print("  - For rejected orders: Reason for rejection")

    client.close()

    print("\n" + "=" * 80)
    print("BATCH PROCESSING (For Multiple IMEIs)")
    print("=" * 80)
    print("\n1. Create a CSV file (orders.csv):")
    print("   imei,network_id")
    print("   123456789012345,1739")
    print("   123456789012346,1739")
    print("   123456789012347,1739")
    print("\n2. Submit batch:")
    print("   python3 gsm_cli.py batch orders.csv --output results.json")
    print("\n3. Results saved to results.json with all order IDs")

    print("\n" + "=" * 80)
    print("REAL-WORLD WORKFLOW")
    print("=" * 80)
    print("""
1. Find service:
   python3 gsm_cli.py services | grep "iPhone"

2. Submit order:
   python3 gsm_cli.py submit 359702373699048 1739

3. Save the Order ID returned (e.g., 54321)

4. Check status (repeat until completed):
   python3 gsm_cli.py status 54321

5. When status shows "Completed", the Code field has your data:
   - Carrier info
   - Simlock status
   - Find My iPhone status
   - Warranty details
   - etc.
""")

if __name__ == "__main__":
    demo_order_flow()
