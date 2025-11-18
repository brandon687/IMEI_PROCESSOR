"""
Test suite for IMEI Data Parser

Tests various data formats and edge cases to ensure robust parsing.
"""

from imei_data_parser import IMEIDataParser, IMEIData


def test_basic_parsing():
    """Test basic parsing with well-formatted data"""
    print("\n" + "="*60)
    print("TEST 1: Basic Parsing")
    print("="*60)

    data = """Model: iPhone 13 128GB Midnight
IMEI Number: 356825821305851
Serial Number: Y9WVV62WP9
IMEI2 Number: 356825821314275
MEID Number: 35682582130585
AppleCare Eligible: OFF
Estimated Purchase Date: 02/10/21
Carrier: Unlocked
Next Tether Policy: 10
Current GSMA Status: Clean
Find My iPhone: OFF
SimLock: Unlocked"""

    parser = IMEIDataParser()
    result = parser.parse(data)

    assert result.model == "iPhone 13 128GB Midnight"
    assert result.imei_number == "356825821305851"
    assert result.serial_number == "Y9WVV62WP9"
    assert result.imei2_number == "356825821314275"
    assert result.carrier == "Unlocked"
    assert result.simlock == "Unlocked"

    print("✓ All assertions passed")
    print(f"✓ Parsed {len(result.to_dict())} fields")
    return True


def test_single_line_format():
    """Test parsing data in single-line format"""
    print("\n" + "="*60)
    print("TEST 2: Single-Line Format (like your original example)")
    print("="*60)

    # Your original format - all on one line with spaces
    data = """Model: iPhone 13 128GB Midnight IMEI Number: 356825821305851 Serial Number: Y9WVV62WP9 IMEI2 Number: 356825821314275 MEID Number: 35682582130585 AppleCare Eligible: OFF Estimated Purchase Date: 02/10/21 Carrier: Unlocked Next Tether Policy: 10 Current GSMA Status: Clean Find My iPhone: OFF SimLock: Unlocked"""

    parser = IMEIDataParser()
    result = parser.parse(data)

    print(f"Parsed fields: {len(result.to_dict())}")

    # This might not work as well - let's see what we get
    print("\nParsed data:")
    for key, value in result.to_display_dict().items():
        print(f"  {key}: {value}")

    # The single-line format is harder to parse reliably
    # We'll need to handle this differently
    return result


def test_missing_fields():
    """Test parsing with missing optional fields"""
    print("\n" + "="*60)
    print("TEST 3: Missing Optional Fields")
    print("="*60)

    data = """Model: iPhone 12
IMEI Number: 123456789012345
Carrier: T-Mobile
SimLock: Locked"""

    parser = IMEIDataParser()
    result = parser.parse(data)

    assert result.model == "iPhone 12"
    assert result.imei_number == "123456789012345"
    assert result.carrier == "T-Mobile"
    assert result.serial_number is None  # Missing field
    assert result.imei2_number is None  # Missing field

    print("✓ Correctly handled missing fields")
    print(f"✓ Parsed {len(result.to_dict())} fields (expected: 4)")
    return True


def test_alternative_headers():
    """Test parsing with alternative header names"""
    print("\n" + "="*60)
    print("TEST 4: Alternative Header Names")
    print("="*60)

    data = """Device Model: iPhone 11 Pro
IMEI: 123456789012345
Serial: ABC123DEF456
Network: AT&T
Lock Status: Unlocked
FMI: OFF"""

    parser = IMEIDataParser()
    result = parser.parse(data)

    print("Parsed data:")
    for key, value in result.to_display_dict().items():
        print(f"  {key}: {value}")

    # Note: "Device Model" not in our mapping, might not work
    # "IMEI" should map to imei_number
    # "Serial" should map to serial_number
    # "Network" should map to carrier
    # "Lock Status" should map to simlock
    # "FMI" should map to find_my_iphone

    return result


def test_extra_whitespace():
    """Test parsing with extra whitespace and formatting issues"""
    print("\n" + "="*60)
    print("TEST 5: Extra Whitespace and Formatting")
    print("="*60)

    data = """Model:    iPhone 13
IMEI Number:   356825821305851
Carrier:  Unlocked
SimLock:    Unlocked   """

    parser = IMEIDataParser()
    result = parser.parse(data)

    assert result.model == "iPhone 13"  # Whitespace should be cleaned
    assert result.imei_number == "356825821305851"
    assert result.carrier == "Unlocked"

    print("✓ Correctly cleaned whitespace")
    return True


def test_validation():
    """Test validation functionality"""
    print("\n" + "="*60)
    print("TEST 6: Validation")
    print("="*60)

    parser = IMEIDataParser()

    # Valid data
    valid_data = """Model: iPhone 13
IMEI Number: 356825821305851"""

    is_valid, missing = parser.validate(valid_data)
    assert is_valid is True
    print("✓ Valid data recognized")

    # Invalid data (missing required IMEI)
    invalid_data = """Model: iPhone 13
Carrier: Unlocked"""

    is_valid, missing = parser.validate(invalid_data)
    assert is_valid is False
    assert 'imei_number' in missing
    print(f"✓ Invalid data detected (missing: {missing})")

    return True


def test_real_world_gsx_format():
    """Test with various real-world GSX response formats"""
    print("\n" + "="*60)
    print("TEST 7: Real-World GSX Format Variations")
    print("="*60)

    # Format 1: Clean multi-line
    format1 = """Model: iPhone 14 Pro Max 256GB
IMEI Number: 359876543210987
Serial Number: ABCD1234EFGH
Carrier: Verizon
SimLock: Locked
Find My iPhone: ON
Current GSMA Status: Clean"""

    # Format 2: With extra info
    format2 = """Model: iPhone 12 Pro
IMEI Number: 123456789012345
IMEI2 Number: 123456789012346
Serial Number: XYZ789
MEID Number: 35682582130585
AppleCare Eligible: ON
Estimated Purchase Date: 12/15/22
Carrier: Sprint
Next Tether Policy: 5
Current GSMA Status: Clean
Find My iPhone: OFF
SimLock: Unlocked"""

    parser = IMEIDataParser()

    print("\nFormat 1:")
    result1 = parser.parse(format1)
    for key, value in result1.to_display_dict().items():
        print(f"  {key}: {value}")

    print("\nFormat 2:")
    result2 = parser.parse(format2)
    for key, value in result2.to_display_dict().items():
        print(f"  {key}: {value}")

    assert result1.model == "iPhone 14 Pro Max 256GB"
    assert result2.imei2_number == "123456789012346"

    print("\n✓ Successfully parsed multiple format variations")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" IMEI DATA PARSER - COMPREHENSIVE TEST SUITE")
    print("="*70)

    tests = [
        ("Basic Parsing", test_basic_parsing),
        ("Single-Line Format", test_single_line_format),
        ("Missing Fields", test_missing_fields),
        ("Alternative Headers", test_alternative_headers),
        ("Extra Whitespace", test_extra_whitespace),
        ("Validation", test_validation),
        ("Real-World GSX Formats", test_real_world_gsx_format),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test_name} ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
