#!/usr/bin/env python3
"""
Generate Test IMEI CSV Files
Creates CSV files with valid IMEI numbers for testing batch submissions
"""

import csv
import random
import sys


def generate_valid_imei():
    """
    Generate a valid IMEI number with proper check digit

    IMEI format: 14 digits + 1 check digit (Luhn algorithm)
    Example: 352130219890307
    """
    # Generate first 14 digits
    # TAC (8 digits) + SNR (6 digits)
    tac = random.randint(35000000, 35999999)  # Typical TAC range
    snr = random.randint(100000, 999999)

    # Combine to get first 14 digits
    imei_14 = f"{tac}{snr}"

    # Calculate check digit using Luhn algorithm
    def luhn_check_digit(number_str):
        """Calculate Luhn check digit"""
        digits = [int(d) for d in number_str]

        # Double every second digit from right to left
        for i in range(len(digits) - 1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

        # Sum all digits
        total = sum(digits)

        # Check digit makes total divisible by 10
        check_digit = (10 - (total % 10)) % 10
        return check_digit

    check_digit = luhn_check_digit(imei_14)

    return f"{imei_14}{check_digit}"


def generate_csv(filename, count):
    """Generate CSV file with IMEI numbers"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['IMEI'])

        # Generate IMEIs
        imeis = set()
        while len(imeis) < count:
            imei = generate_valid_imei()
            imeis.add(imei)

        # Write IMEIs
        for imei in sorted(imeis):
            writer.writerow([imei])

    print(f"✅ Generated {count} IMEIs in {filename}")


def main():
    """Generate test CSV files for various batch sizes"""
    print("="*80)
    print("GENERATING TEST IMEI FILES")
    print("="*80)

    test_volumes = [
        (4, 'test_4_imeis.csv', 'Small test - verify speed (~1-2 seconds)'),
        (10, 'test_10_imeis.csv', 'Quick test - verify batch processing'),
        (100, 'test_100_imeis.csv', 'Medium test - verify parallel processing (~3-5 seconds)'),
        (1000, 'test_1000_imeis.csv', 'Large test - verify scale (~5-8 seconds)'),
        (6000, 'test_6000_imeis.csv', 'Daily volume test - real-world scenario (~7-10 seconds)'),
    ]

    # Allow custom volume from command line
    if len(sys.argv) > 1:
        try:
            custom_count = int(sys.argv[1])
            custom_filename = f'test_{custom_count}_imeis.csv'
            print(f"\n📝 Generating custom volume: {custom_count} IMEIs")
            generate_csv(custom_filename, custom_count)
            print(f"\n✅ Created {custom_filename}")
            return
        except ValueError:
            print("❌ Invalid number. Usage: python3 generate_test_imeis.py [count]")
            return

    # Generate all standard test files
    print("\n📝 Generating standard test files...\n")

    for count, filename, description in test_volumes:
        print(f"Generating {filename}...")
        generate_csv(filename, count)
        print(f"   Purpose: {description}\n")

    print("="*80)
    print("TEST FILES GENERATED")
    print("="*80)

    print("\nHow to use these files:")
    print("\n1. Start web server:")
    print("   python3 web_app.py")

    print("\n2. Test with small batch (4 IMEIs):")
    print("   - Go to http://localhost:5001/batch")
    print("   - Upload: test_4_imeis.csv")
    print("   - Expected: Complete in 1-2 seconds")

    print("\n3. Test with medium batch (100 IMEIs):")
    print("   - Upload: test_100_imeis.csv")
    print("   - Expected: Complete in 3-5 seconds")

    print("\n4. Test with large batch (1,000 IMEIs):")
    print("   - Upload: test_1000_imeis.csv")
    print("   - Expected: Complete in 5-8 seconds")

    print("\n5. Test with daily volume (6,000 IMEIs):")
    print("   - Upload: test_6000_imeis.csv")
    print("   - Expected: Complete in 7-10 seconds")

    print("\n⚠️  NOTE: These are test IMEIs and may not exist in carrier databases.")
    print("   GSM Fusion may return errors for unknown IMEIs.")
    print("   The important metric is SPEED, not success rate.")

    print("\n📊 Monitor logs during testing:")
    print("   tail -f /tmp/production_submission.log")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
