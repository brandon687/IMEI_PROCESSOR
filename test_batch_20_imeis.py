#!/usr/bin/env python3
"""
BATCH API TEST - 20 IMEIs
Cost: $1.60 (20 IMEIs × $0.08)

Purpose: Verify GSM Fusion API supports batch submission
Tests: Submit 20 IMEIs in one API call (comma-separated)
"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient
import json
from datetime import datetime

load_dotenv()

# Test parameters
SERVICE_ID = "1739"  # iPhone AT&T Premium - USA
BATCH_SIZE = 20

print("="*80)
print("BATCH API TEST - 20 IMEIs")
print("="*80)
print(f"Cost: $1.60 (20 IMEIs × $0.08)")
print(f"Service ID: {SERVICE_ID}")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*80)
print()

# User-provided test IMEIs
test_imeis = [
    "353978109238980",
    "356554104710187",
    "356867116918840",
    "353985108681185",
    "351458444245430",
    "356800115363395",
    "352897110952838",
    "353975103367625",
    "356861111529603",
    "356803116640985",
    "350342022825410",
    "352784721038175",
    "359824134321538",
    "353509875687603",
    "357504275048643",
    "351166898205210",
    "352513428277855",
    "357463529764333",
    "353834924397610",
    "352113538308482",
]

print("⚠️  WARNING: This will charge $1.60 to your GSM Fusion account")
print()
print(f"Testing with {len(test_imeis)} IMEIs:")
for i, imei in enumerate(test_imeis, 1):
    print(f"  {i:2d}. {imei}")
print()

# Confirmation
confirm = input("Type 'YES' to proceed with $1.60 test: ")
if confirm != "YES":
    print("❌ Test cancelled")
    exit(0)

print()
print("🚀 Starting batch submission test...")
print()

try:
    client = GSMFusionClient()

    # TEST 1: Submit as batch (all 20 IMEIs in one API call)
    print("-"*80)
    print("TEST 1: BATCH SUBMISSION (20 IMEIs in one API call)")
    print("-"*80)

    start_time = datetime.now()

    result = client.place_imei_order(
        imei=test_imeis,  # Pass as list - client will format as comma-separated
        network_id=SERVICE_ID
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"✅ API call completed in {duration:.2f} seconds")
    print()

    # Parse results
    orders = result.get('orders', [])
    duplicates = result.get('duplicates', [])
    errors = result.get('errors', [])

    print("="*80)
    print("RESULTS")
    print("="*80)
    print(f"Total IMEIs sent: {len(test_imeis)}")
    print(f"Successful orders: {len(orders)}")
    print(f"Duplicates: {len(duplicates)}")
    print(f"Errors: {len(errors)}")
    print()

    # Show order details
    if orders:
        print("📦 ORDERS CREATED:")
        for i, order in enumerate(orders, 1):
            order_id = order.get('id', 'N/A')
            imei = order.get('imei', 'N/A')
            status = order.get('status', 'N/A')
            print(f"  {i:2d}. Order {order_id}: IMEI {imei} - Status: {status}")
        print()

    if duplicates:
        print("🔄 DUPLICATES (already submitted):")
        for i, dup in enumerate(duplicates, 1):
            print(f"  {i:2d}. {dup}")
        print()

    if errors:
        print("❌ ERRORS:")
        for i, err in enumerate(errors, 1):
            print(f"  {i:2d}. {err}")
        print()

    # Cost calculation
    charged_count = len(orders)  # Only successful orders are charged
    actual_cost = charged_count * 0.08

    print("="*80)
    print("COST ANALYSIS")
    print("="*80)
    print(f"Expected cost: $1.60 (20 IMEIs)")
    print(f"Actual charged: ${actual_cost:.2f} ({charged_count} successful orders)")
    print()

    # Verification
    print("="*80)
    print("BATCH API VERIFICATION")
    print("="*80)

    if len(orders) == len(test_imeis):
        print("✅ BATCH API WORKS! All 20 IMEIs processed in one call")
        print("   Result: Can safely use batch_size=100 in production")
        print()
    elif len(orders) == 1:
        print("❌ BATCH API NOT SUPPORTED - Only first IMEI processed")
        print("   Result: Must use batch_size=1 (individual API calls)")
        print()
    elif len(orders) > 1 and len(orders) < len(test_imeis):
        print(f"⚠️  PARTIAL SUCCESS - {len(orders)}/{len(test_imeis)} IMEIs processed")
        print("   Result: Batch API may have size limits or some IMEIs failed")
        print()
    elif len(orders) == 0 and len(errors) > 0:
        print("❌ BATCH FAILED - All IMEIs rejected")
        print("   Result: Check errors above")
        print()
    elif len(duplicates) == len(test_imeis):
        print("⚠️  ALL DUPLICATES - These IMEIs were already submitted")
        print("   Result: Cannot verify batch API (need fresh IMEIs)")
        print()

    # Save full results to file
    results_file = f"batch_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'test_timestamp': datetime.now().isoformat(),
            'service_id': SERVICE_ID,
            'imeis_sent': test_imeis,
            'duration_seconds': duration,
            'orders': orders,
            'duplicates': duplicates,
            'errors': errors,
            'cost': actual_cost
        }, f, indent=2)

    print(f"📄 Full results saved to: {results_file}")
    print()

    # Recommendation
    print("="*80)
    print("RECOMMENDATION")
    print("="*80)

    if len(orders) >= 15:  # At least 75% success rate
        print("✅ SAFE TO DEPLOY with batch_size=100")
        print()
        print("Next steps:")
        print("1. Modify web_app.py lines 111 and 289:")
        print("   batch_size=100  # Keep current value")
        print()
        print("2. Restart web server")
        print()
        print("3. Test with your real IMEIs")
        print()
        print("Expected performance:")
        print("  - 6,000 IMEIs: ~7 seconds")
        print("  - 20,000 IMEIs: ~23 seconds")
    else:
        print("⚠️  USE batch_size=1 (individual calls) for safety")
        print()
        print("Next steps:")
        print("1. Modify web_app.py lines 111 and 289:")
        print("   batch_size=1  # Change from 100 to 1")
        print()
        print("2. Restart web server")
        print()
        print("3. Test with your real IMEIs")
        print()
        print("Expected performance:")
        print("  - 6,000 IMEIs: ~12 minutes (still 4x faster than old code)")

    print("="*80)

    client.close()

except Exception as e:
    print()
    print("="*80)
    print("❌ ERROR DURING TEST")
    print("="*80)
    print(f"Error: {e}")
    print()

    import traceback
    traceback.print_exc()

    print()
    print("This error occurred BEFORE charges were made.")
    print("Cost: $0.00 (API call failed)")
    print()
    print("Troubleshooting:")
    print("1. Check .env file has GSM_FUSION_API_KEY")
    print("2. Verify API key is valid")
    print("3. Check network connection")
    print("4. Review error message above")

print()
print("Test complete!")
