"""
Integration Example: Using IMEI Data Parser with HAMMER-API

This demonstrates how to integrate the parser with:
1. GSM Fusion API responses
2. Database storage
3. Web interface display
"""

from imei_data_parser import IMEIDataParser, IMEIData
from database import IMEIDatabase, get_database
from typing import Dict, Any
import json


# ============================================================
# EXAMPLE 1: Parse GSM Fusion API Response
# ============================================================

def parse_gsm_fusion_response(raw_response: str) -> IMEIData:
    """
    Parse raw response from GSM Fusion API

    Args:
        raw_response: Raw text response from API

    Returns:
        Structured IMEIData object

    Example:
        >>> response = "Model: iPhone 13 IMEI Number: 123..."
        >>> data = parse_gsm_fusion_response(response)
        >>> print(data.model)
        'iPhone 13'
    """
    parser = IMEIDataParser()
    return parser.parse(raw_response)


# ============================================================
# EXAMPLE 2: Store Parsed Data in Database
# ============================================================

def store_parsed_imei_data(parsed_data: IMEIData, order_id: str,
                          service_id: str, credits: float) -> bool:
    """
    Store parsed IMEI data in the local database

    Args:
        parsed_data: Parsed IMEIData object
        order_id: GSM Fusion order ID
        service_id: Service package ID
        credits: Cost in credits

    Returns:
        True if stored successfully
    """
    db = get_database()

    # Convert parsed data to database format
    order_data = {
        'order_id': order_id,
        'service_id': service_id,
        'imei': parsed_data.imei_number,
        'imei2': parsed_data.imei2_number,
        'credits': credits,
        'status': 'Completed',
        'carrier': parsed_data.carrier,
        'simlock': parsed_data.simlock,
        'model': parsed_data.model,
        'fmi': parsed_data.find_my_iphone,
        'serial_number': parsed_data.serial_number,
        'meid': parsed_data.meid_number,
        'gsma_status': parsed_data.current_gsma_status,
        'purchase_date': parsed_data.estimated_purchase_date,
        'applecare': parsed_data.applecare_eligible,
        'tether_policy': parsed_data.next_tether_policy,
        'result_code': 'SUCCESS',
        'notes': 'Parsed from GSX response'
    }

    try:
        db.insert_order(order_data)
        return True
    except Exception as e:
        print(f"Error storing data: {e}")
        return False


# ============================================================
# EXAMPLE 3: Extract Data for Web Display
# ============================================================

def format_for_web_display(parsed_data: IMEIData) -> Dict[str, Any]:
    """
    Format parsed data for web interface display

    Args:
        parsed_data: Parsed IMEIData object

    Returns:
        Dictionary formatted for HTML template rendering

    Example:
        >>> data = parse_gsm_fusion_response(response)
        >>> web_data = format_for_web_display(data)
        >>> # Use in Flask: render_template('status.html', **web_data)
    """
    display_data = parsed_data.to_display_dict()

    # Add status badges/colors based on values
    status_info = {
        'simlock_class': 'success' if parsed_data.simlock == 'Unlocked' else 'danger',
        'fmi_class': 'success' if parsed_data.find_my_iphone == 'OFF' else 'danger',
        'gsma_class': 'success' if parsed_data.current_gsma_status == 'Clean' else 'warning',
    }

    return {
        'data': display_data,
        'status': status_info
    }


# ============================================================
# EXAMPLE 4: Batch Processing with Parser
# ============================================================

def process_batch_responses(responses: list[tuple[str, str]]) -> list[IMEIData]:
    """
    Process multiple API responses at once

    Args:
        responses: List of (order_id, raw_response) tuples

    Returns:
        List of parsed IMEIData objects

    Example:
        >>> responses = [
        ...     ("12345", "Model: iPhone 13..."),
        ...     ("12346", "Model: iPhone 12..."),
        ... ]
        >>> results = process_batch_responses(responses)
        >>> print(f"Processed {len(results)} orders")
    """
    parser = IMEIDataParser()
    results = []

    for order_id, raw_response in responses:
        try:
            parsed = parser.parse(raw_response)
            results.append(parsed)
        except Exception as e:
            print(f"Error parsing order {order_id}: {e}")
            continue

    return results


# ============================================================
# EXAMPLE 5: Export Parsed Data to CSV
# ============================================================

def export_to_csv(parsed_data_list: list[IMEIData], filename: str = 'export.csv'):
    """
    Export parsed data to CSV file

    Args:
        parsed_data_list: List of parsed IMEIData objects
        filename: Output CSV filename
    """
    import csv

    if not parsed_data_list:
        print("No data to export")
        return

    # Get all field names from first item
    fieldnames = list(parsed_data_list[0].to_display_dict().keys())

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for data in parsed_data_list:
            writer.writerow(data.to_display_dict())

    print(f"Exported {len(parsed_data_list)} records to {filename}")


# ============================================================
# EXAMPLE 6: Compare Expected vs Actual Data
# ============================================================

def validate_imei_data(parsed_data: IMEIData, expected_imei: str) -> Dict[str, Any]:
    """
    Validate parsed data against expected values

    Args:
        parsed_data: Parsed IMEIData object
        expected_imei: IMEI that was originally submitted

    Returns:
        Validation result dictionary

    Example:
        >>> result = validate_imei_data(data, "123456789012345")
        >>> if result['valid']:
        ...     print("Data matches expected IMEI")
    """
    validation = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # Check if IMEI matches
    if parsed_data.imei_number != expected_imei:
        validation['valid'] = False
        validation['errors'].append(
            f"IMEI mismatch: expected {expected_imei}, got {parsed_data.imei_number}"
        )

    # Check for required fields
    if not parsed_data.model:
        validation['warnings'].append("Model information missing")

    if not parsed_data.carrier:
        validation['warnings'].append("Carrier information missing")

    # Check for suspicious values
    if parsed_data.find_my_iphone == 'ON':
        validation['warnings'].append("Find My iPhone is ON - device may be locked")

    if parsed_data.current_gsma_status and parsed_data.current_gsma_status != 'Clean':
        validation['warnings'].append(
            f"GSMA Status: {parsed_data.current_gsma_status} - possible issue"
        )

    return validation


# ============================================================
# EXAMPLE 7: Full Integration Demo
# ============================================================

def full_integration_demo():
    """
    Complete integration example showing real-world usage
    """
    print("="*70)
    print("IMEI DATA PARSER - FULL INTEGRATION DEMO")
    print("="*70)

    # Step 1: Simulate API response
    print("\n1. Simulating GSM Fusion API response...")
    api_response = """Model: iPhone 13 128GB Midnight
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

    # Step 2: Parse the response
    print("2. Parsing response...")
    parsed = parse_gsm_fusion_response(api_response)
    print(f"   ✓ Parsed {len(parsed.to_dict())} fields")

    # Step 3: Validate data
    print("\n3. Validating data...")
    validation = validate_imei_data(parsed, "356825821305851")
    if validation['valid']:
        print("   ✓ Data validation passed")
    else:
        print(f"   ✗ Validation errors: {validation['errors']}")

    if validation['warnings']:
        print(f"   ⚠ Warnings: {validation['warnings']}")

    # Step 4: Format for display
    print("\n4. Formatting for web display...")
    web_data = format_for_web_display(parsed)
    print("   ✓ Web display data:")
    for key, value in web_data['data'].items():
        print(f"     - {key}: {value}")

    # Step 5: Store in database (commented out - requires database setup)
    print("\n5. Database storage...")
    print("   ℹ Skipping database storage (demo mode)")
    # store_parsed_imei_data(parsed, "12345678", "1", 0.50)

    # Step 6: Export to JSON
    print("\n6. Exporting to JSON...")
    json_export = json.dumps(parsed.to_dict(), indent=2)
    print("   ✓ JSON export:")
    print("   " + json_export.replace("\n", "\n   "))

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


# ============================================================
# EXAMPLE 8: Integration with gsm_fusion_client.py
# ============================================================

def integrate_with_gsm_client():
    """
    Show how to integrate parser with GSMFusionClient

    Add this to your gsm_fusion_client.py or web_app.py:
    """
    example_code = '''
# In gsm_fusion_client.py or web_app.py:

from imei_data_parser import IMEIDataParser

class GSMFusionClient:
    def __init__(self):
        # ... existing code ...
        self.parser = IMEIDataParser()

    def get_imei_orders(self, order_ids):
        """Fetch and parse order details"""
        # ... existing API call code ...
        response = self._make_request('/getimeis', {'id': order_ids})

        # NEW: Parse each order's response
        for order in response.get('data', []):
            raw_response = order.get('information', '')
            if raw_response:
                # Parse the response
                parsed_data = self.parser.parse(raw_response)

                # Add parsed fields to order dict
                order['parsed'] = parsed_data.to_dict()

        return response
'''

    print("="*70)
    print("INTEGRATION WITH GSMFusionClient")
    print("="*70)
    print(example_code)


if __name__ == "__main__":
    # Run the full demo
    full_integration_demo()

    print("\n\n")

    # Show integration code
    integrate_with_gsm_client()
