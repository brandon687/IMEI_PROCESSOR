#!/usr/bin/env python3
"""
Demo using YOUR EXACT example data

This demonstrates the parser working with the exact format you provided.
"""

from imei_data_parser import IMEIDataParser
import json


def main():
    print("="*70)
    print("PARSING YOUR EXACT EXAMPLE DATA")
    print("="*70)

    # Your exact example (single-line format)
    your_data = """Model: iPhone 13 128GB Midnight IMEI Number: 356825821305851 Serial Number: Y9WVV62WP9 IMEI2 Number: 356825821314275 MEID Number: 35682582130585 AppleCare Eligible: OFF Estimated Purchase Date: 02/10/21 Carrier: Unlocked Next Tether Policy: 10 Current GSMA Status: Clean Find My iPhone: OFF SimLock: Unlocked"""

    print("\n📥 INPUT (single-line format):")
    print("-" * 70)
    print(your_data[:100] + "...")
    print("-" * 70)

    # Initialize parser
    parser = IMEIDataParser()

    # Parse the data
    result = parser.parse(your_data)

    print("\n✅ SUCCESSFULLY PARSED!")
    print(f"Found {len(result.to_dict())} fields\n")

    # Show the extracted headers and data
    print("📋 EXTRACTED HEADERS AND DATA:")
    print("=" * 70)

    display_data = result.to_display_dict()

    # Print in a nice format
    max_header_len = max(len(k) for k in display_data.keys())

    for header, value in display_data.items():
        print(f"{header:<{max_header_len}} : {value}")

    print("=" * 70)

    # Show how to access individual fields
    print("\n🎯 ACCESSING INDIVIDUAL FIELDS:")
    print("-" * 70)
    print(f"result.model              = '{result.model}'")
    print(f"result.imei_number        = '{result.imei_number}'")
    print(f"result.serial_number      = '{result.serial_number}'")
    print(f"result.imei2_number       = '{result.imei2_number}'")
    print(f"result.meid_number        = '{result.meid_number}'")
    print(f"result.applecare_eligible = '{result.applecare_eligible}'")
    print(f"result.estimated_purchase_date = '{result.estimated_purchase_date}'")
    print(f"result.carrier            = '{result.carrier}'")
    print(f"result.next_tether_policy = '{result.next_tether_policy}'")
    print(f"result.current_gsma_status = '{result.current_gsma_status}'")
    print(f"result.find_my_iphone     = '{result.find_my_iphone}'")
    print(f"result.simlock            = '{result.simlock}'")
    print("-" * 70)

    # Show as Python dictionary
    print("\n📦 AS PYTHON DICTIONARY (snake_case keys):")
    print("-" * 70)
    data_dict = result.to_dict()
    for key, value in data_dict.items():
        print(f"  '{key}': '{value}',")
    print("-" * 70)

    # Show as JSON
    print("\n📄 AS JSON:")
    print("-" * 70)
    json_output = json.dumps(result.to_dict(), indent=2)
    print(json_output)
    print("-" * 70)

    # Show validation
    print("\n✓ VALIDATION:")
    print("-" * 70)
    is_valid, missing = parser.validate(your_data)
    if is_valid:
        print("✓ All required fields present (Model, IMEI Number)")
    else:
        print(f"✗ Missing required fields: {missing}")
    print("-" * 70)

    # Show device status summary
    print("\n📱 DEVICE STATUS SUMMARY:")
    print("-" * 70)
    print(f"Device: {result.model}")
    print(f"IMEI: {result.imei_number}")
    print(f"Serial: {result.serial_number}")
    print()
    print(f"Carrier Status: {result.carrier}")
    simlock_icon = "🔓" if result.simlock == "Unlocked" else "🔒"
    print(f"SIM Lock: {simlock_icon} {result.simlock}")
    print()
    fmi_icon = "✅" if result.find_my_iphone == "OFF" else "⚠️"
    print(f"Find My iPhone: {fmi_icon} {result.find_my_iphone}")
    gsma_icon = "✅" if result.current_gsma_status == "Clean" else "⚠️"
    print(f"GSMA Status: {gsma_icon} {result.current_gsma_status}")
    print()
    print(f"AppleCare: {result.applecare_eligible}")
    print(f"Purchase Date: {result.estimated_purchase_date}")
    print("-" * 70)

    # Show how to use in real scenarios
    print("\n💡 USAGE EXAMPLES:")
    print("=" * 70)

    print("\n1️⃣  Store in database:")
    print("""
    db.insert_order({
        'order_id': '12345678',
        'imei': result.imei_number,
        'model': result.model,
        'carrier': result.carrier,
        'simlock': result.simlock,
        'fmi': result.find_my_iphone,
        'serial_number': result.serial_number,
        # ... other fields
    })
    """)

    print("\n2️⃣  Check device status:")
    print("""
    if result.simlock == 'Unlocked':
        print("✓ Device is unlocked!")

    if result.find_my_iphone == 'OFF':
        print("✓ Find My iPhone is disabled")

    if result.current_gsma_status == 'Clean':
        print("✓ Device is not blacklisted")
    """)

    print("\n3️⃣  Export to CSV:")
    print("""
    import csv
    with open('export.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=result.to_dict().keys())
        writer.writeheader()
        writer.writerow(result.to_dict())
    """)

    print("\n4️⃣  Display in web interface:")
    print("""
    @app.route('/order/<order_id>')
    def view_order(order_id):
        order = db.get_order(order_id)
        result = parser.parse(order['raw_response'])

        return render_template('order.html',
                              details=result.to_display_dict())
    """)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE - Parser ready to use!")
    print("=" * 70)

    # Quick comparison
    print("\n📊 COMPARISON:")
    print("=" * 70)
    print("Without Parser:")
    print("  - Manual string splitting")
    print("  - Regex patterns for each field")
    print("  - 100+ lines of fragile code")
    print("  - Breaks with format changes")
    print()
    print("With Parser:")
    print("  ✓ One line: parser.parse(data)")
    print("  ✓ Handles multiple formats automatically")
    print("  ✓ Clean, structured output")
    print("  ✓ Validated and tested")
    print("=" * 70)


if __name__ == "__main__":
    main()
