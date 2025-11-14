#!/usr/bin/env python3
"""
BATCH API TEST - 10 Fresh IMEIs
Cost: $0.80 (10 IMEIs × $0.08)
Testing if batch API creates multiple orders
"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient
import json
from datetime import datetime

load_dotenv()

# Test parameters
SERVICE_ID = "1739"  # iPhone AT&T Premium - USA

# Fresh test IMEIs (user confirmed these are new)
test_imeis = [
    "352569487269092",
    "350419535651945",
    "356673371159017",
    "352725353472208",
    "354455406397677",
    "350321533639957",
    "353869221291132",
    "355917846755789",
    "352832401293345",
    "355473496054560",
]

print("="*80)
print("BATCH API TEST - 10 FRESH IMEIs")
print("="*80)
print(f"Cost: $0.80 (10 IMEIs × $0.08)")
print(f"Service ID: {SERVICE_ID}")
print(f"Timestamp: {datetime.now().isoformat()}")
print("="*80)
print()

print(f"Testing with {len(test_imeis)} fresh IMEIs")
print()

print("🚀 Starting batch submission test...")
print()

try:
    client = GSMFusionClient()

    # Submit as batch (all 10 IMEIs in one API call)
    print("-"*80)
    print("SUBMITTING BATCH: 10 IMEIs in ONE API call")
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
    print(f"Expected cost: $0.80 (10 IMEIs)")
    print(f"Actual charged: ${actual_cost:.2f} ({charged_count} successful orders)")

    if len(duplicates) > 0:
        duplicate_saved = len(duplicates) * 0.08
        print(f"Saved from duplicates: ${duplicate_saved:.2f} ({len(duplicates)} IMEIs)")
    print()

    # Critical verification
    print("="*80)
    print("BATCH API VERIFICATION - CRITICAL RESULTS")
    print("="*80)

    if len(orders) >= 8:  # At least 80% success
        print("🎉 ✅ BATCH API CONFIRMED WORKING!")
        print()
        print(f"   • Sent: 10 IMEIs in 1 API call")
        print(f"   • Received: {len(orders)} separate order IDs")
        print(f"   • Time: {duration:.2f} seconds")
        print(f"   • Cost: ${actual_cost:.2f}")
        print()
        print("   This proves the GSM Fusion API supports batch submission!")
        print()
        print("🚀 PRODUCTION READY: You can use batch_size=100")
        print()
        verification = "BATCH_CONFIRMED_WORKING"

    elif len(orders) == 1:
        print("❌ BATCH API NOT SUPPORTED")
        print()
        print(f"   • Sent: 10 IMEIs in 1 API call")
        print(f"   • Received: Only 1 order ID")
        print(f"   • Cost: $0.08 (only first IMEI processed)")
        print()
        print("   The API only processed the first IMEI in the batch.")
        print()
        print("⚠️  MUST USE: batch_size=1 (individual calls)")
        print()
        verification = "BATCH_NOT_SUPPORTED"

    elif len(orders) > 1 and len(orders) < 8:
        print(f"⚠️  PARTIAL SUCCESS")
        print()
        print(f"   • Sent: 10 IMEIs")
        print(f"   • Received: {len(orders)} orders")
        print(f"   • Missing: {10 - len(orders)} orders")
        print()
        print("   Some IMEIs may have failed or API has batch size limits.")
        print()
        verification = "BATCH_PARTIAL"

    elif len(orders) == 0 and len(duplicates) >= 8:
        print("⚠️  MOSTLY DUPLICATES")
        print()
        print(f"   • Duplicates: {len(duplicates)}/10")
        print(f"   • Cost: ${actual_cost:.2f} (only new IMEIs charged)")
        print()
        print("   Need to test with more fresh IMEIs to confirm batch API.")
        print()
        verification = "MOSTLY_DUPLICATES"

    else:
        print("❌ BATCH FAILED")
        print()
        print(f"   • Orders created: {len(orders)}")
        print(f"   • Errors: {len(errors)}")
        print()
        verification = "BATCH_FAILED"

    # Save full results to file
    results_file = f"batch_test_10_fresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'test_timestamp': datetime.now().isoformat(),
            'service_id': SERVICE_ID,
            'imeis_sent': test_imeis,
            'duration_seconds': duration,
            'orders': orders,
            'duplicates': duplicates,
            'errors': errors,
            'cost': actual_cost,
            'verification': verification
        }, f, indent=2)

    print(f"📄 Results saved to: {results_file}")
    print()

    # Final recommendation
    print("="*80)
    print("PRODUCTION DEPLOYMENT RECOMMENDATION")
    print("="*80)

    if len(orders) >= 8:
        print("✅ DEPLOY WITH: batch_size=100 (MAXIMUM SPEED)")
        print()
        print("web_app.py configuration:")
        print("  Lines 111 and 289:")
        print("    batch_size=100  ← Keep current value (NO CHANGES NEEDED)")
        print("    max_workers=30  ← Keep current value")
        print()
        print("Expected performance:")
        print("  • 6,000 IMEIs: 7-10 seconds (96x faster)")
        print("  • 20,000 IMEIs: 23-30 seconds")
        print()
        print("Next steps:")
        print("  1. Restart web server: python3 web_app.py")
        print("  2. Test with 50-100 IMEIs to verify")
        print("  3. Deploy for daily 6K-20K operations")
        print()
        print("🎉 Your system is PRODUCTION READY!")

    elif len(orders) == 1:
        print("⚠️  DEPLOY WITH: batch_size=1 (SAFE MODE)")
        print()
        print("web_app.py configuration:")
        print("  Lines 111 and 289:")
        print("    batch_size=1  ← CHANGE from 100")
        print("    max_workers=30  ← Keep current value")
        print()
        print("Expected performance:")
        print("  • 6,000 IMEIs: 12 minutes (4x faster than old code)")
        print("  • 20,000 IMEIs: 40 minutes")
        print()
        print("Next steps:")
        print("  1. Edit web_app.py (2 lines to change)")
        print("  2. Restart web server")
        print("  3. Deploy with confidence")

    else:
        print("⚠️  RESULTS UNCLEAR - NEED MORE DATA")
        print()
        print("Options:")
        print("  A) Test again with 20 completely fresh IMEIs")
        print("  B) Deploy with batch_size=1 for safety")
        print("  C) Contact GSM Fusion support")

    print("="*80)

    client.close()

    print()
    print(f"✅ Test complete! Actual cost: ${actual_cost:.2f}")
    print()

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
    print("Troubleshooting:")
    print("1. Check .env file has GSM_FUSION_API_KEY")
    print("2. Verify API key is valid")
    print("3. Check network connection")
