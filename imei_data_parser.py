"""
IMEI Data Parser - Extracts structured data from GSX/IMEI service responses

This parser handles semi-structured text data from IMEI lookup services
and extracts key-value pairs based on predefined headers.

Usage:
    parser = IMEIDataParser()
    result = parser.parse(raw_text_data)
    print(result.to_dict())
"""

import re
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class IMEIData:
    """Structured representation of IMEI lookup data"""
    model: Optional[str] = None
    imei_number: Optional[str] = None
    serial_number: Optional[str] = None
    imei2_number: Optional[str] = None
    meid_number: Optional[str] = None
    applecare_eligible: Optional[str] = None
    estimated_purchase_date: Optional[str] = None
    carrier: Optional[str] = None
    next_tether_policy: Optional[str] = None
    current_gsma_status: Optional[str] = None
    find_my_iphone: Optional[str] = None
    simlock: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_display_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with human-readable keys"""
        field_mapping = {
            'model': 'Model',
            'imei_number': 'IMEI Number',
            'serial_number': 'Serial Number',
            'imei2_number': 'IMEI2 Number',
            'meid_number': 'MEID Number',
            'applecare_eligible': 'AppleCare Eligible',
            'estimated_purchase_date': 'Estimated Purchase Date',
            'carrier': 'Carrier',
            'next_tether_policy': 'Next Tether Policy',
            'current_gsma_status': 'Current GSMA Status',
            'find_my_iphone': 'Find My iPhone',
            'simlock': 'SimLock'
        }
        return {field_mapping.get(k, k): v
                for k, v in asdict(self).items() if v is not None}


class IMEIDataParser:
    """
    Parser for semi-structured IMEI data from GSX/IMEI services

    Handles various formats:
    - "Header: Value" format
    - Multi-line values
    - Variations in spacing and casing
    """

    # Define expected headers and their normalized field names
    HEADER_MAPPING = {
        'model': ['model', 'device model', 'model name'],
        'imei_number': ['imei number', 'imei', 'imei1'],
        'serial_number': ['serial number', 'serial', 'sn'],
        'imei2_number': ['imei2 number', 'imei2', 'imei 2'],
        'meid_number': ['meid number', 'meid'],
        'applecare_eligible': ['applecare eligible', 'applecare', 'apple care'],
        'estimated_purchase_date': ['estimated purchase date', 'purchase date', 'bought date'],
        'carrier': ['carrier', 'network', 'operator'],
        'next_tether_policy': ['next tether policy', 'tether policy', 'policy id'],
        'current_gsma_status': ['current gsma status', 'gsma status', 'blacklist status'],
        'find_my_iphone': ['find my iphone', 'fmi', 'find my', 'icloud'],
        'simlock': ['simlock', 'sim lock', 'lock status']
    }

    def __init__(self):
        """Initialize the parser with compiled regex patterns"""
        # Build reverse mapping: variation -> field_name
        self.header_to_field = {}
        for field_name, variations in self.HEADER_MAPPING.items():
            for variation in variations:
                self.header_to_field[variation.lower()] = field_name

        # Compile regex for "Header: Value" pattern
        # Captures header and value, handles multi-line values
        self.pattern = re.compile(
            r'^([A-Za-z0-9\s]+?):\s*(.+?)(?=\n[A-Za-z0-9\s]+?:|$)',
            re.MULTILINE | re.DOTALL
        )

    def normalize_header(self, header: str) -> Optional[str]:
        """
        Normalize a header string to its field name

        Args:
            header: Raw header string (e.g., "IMEI Number", "imei_number")

        Returns:
            Normalized field name or None if not recognized
        """
        header_clean = header.strip().lower()
        return self.header_to_field.get(header_clean)

    def clean_value(self, value: str) -> str:
        """
        Clean and normalize a value string

        Args:
            value: Raw value string

        Returns:
            Cleaned value string
        """
        # Remove extra whitespace and newlines
        value = ' '.join(value.split())
        # Strip leading/trailing whitespace
        value = value.strip()
        return value

    def parse(self, raw_data: str) -> IMEIData:
        """
        Parse raw IMEI data text into structured IMEIData object

        Args:
            raw_data: Raw text data from IMEI service

        Returns:
            IMEIData object with parsed fields

        Example:
            >>> parser = IMEIDataParser()
            >>> data = parser.parse(response_text)
            >>> print(data.model)
            'iPhone 13 128GB Midnight'
        """
        if not raw_data:
            return IMEIData()

        # First, try to detect if this is single-line format
        # (no newlines, just spaces between "Header: Value" pairs)
        if '\n' not in raw_data and len(raw_data) > 100:
            # Likely single-line format - preprocess it
            raw_data = self._preprocess_single_line(raw_data)

        # Find all "Header: Value" pairs
        matches = self.pattern.findall(raw_data)

        parsed_data = {}

        for header, value in matches:
            # Normalize the header to field name
            field_name = self.normalize_header(header)

            if field_name:
                # Clean the value
                clean_val = self.clean_value(value)

                # Store in parsed data
                if clean_val:  # Only store non-empty values
                    parsed_data[field_name] = clean_val

        # Create IMEIData object with parsed data
        return IMEIData(**parsed_data)

    def _preprocess_single_line(self, data: str) -> str:
        """
        Convert single-line format to multi-line format

        Converts: "Model: iPhone 13 IMEI Number: 123 Serial: ABC"
        To: "Model: iPhone 13\nIMEI Number: 123\nSerial: ABC"

        Args:
            data: Single-line formatted data

        Returns:
            Multi-line formatted data
        """
        # Build a pattern that matches known headers
        all_headers = []
        for variations in self.HEADER_MAPPING.values():
            all_headers.extend(variations)

        # Add the actual headers we expect
        expected_headers = [
            'Model', 'IMEI Number', 'Serial Number', 'IMEI2 Number',
            'MEID Number', 'AppleCare Eligible', 'Estimated Purchase Date',
            'Carrier', 'Next Tether Policy', 'Current GSMA Status',
            'Find My iPhone', 'SimLock'
        ]

        # Sort by length (longest first) to avoid partial matches
        expected_headers.sort(key=len, reverse=True)

        # Replace " Header:" with "\nHeader:" for each known header
        result = data
        for header in expected_headers:
            # Look for " Header:" (space before header, colon after)
            # But not at the start of the string
            result = re.sub(
                r'(?<!^)(\s+)(' + re.escape(header) + r':)',
                r'\n\2',
                result,
                flags=re.IGNORECASE
            )

        return result

    def parse_to_dict(self, raw_data: str) -> Dict[str, Any]:
        """
        Parse raw data and return as dictionary

        Args:
            raw_data: Raw text data from IMEI service

        Returns:
            Dictionary with parsed fields
        """
        return self.parse(raw_data).to_dict()

    def extract_headers(self, raw_data: str) -> list[str]:
        """
        Extract all headers found in the raw data

        Args:
            raw_data: Raw text data

        Returns:
            List of header strings found
        """
        matches = self.pattern.findall(raw_data)
        return [header.strip() for header, _ in matches]

    def validate(self, raw_data: str) -> tuple[bool, list[str]]:
        """
        Validate that all expected headers are present

        Args:
            raw_data: Raw text data

        Returns:
            Tuple of (is_valid, missing_headers)
        """
        parsed = self.parse(raw_data)
        parsed_dict = parsed.to_dict()

        # Define required fields (adjust based on your needs)
        required_fields = ['imei_number', 'model']

        missing = [field for field in required_fields
                   if field not in parsed_dict or not parsed_dict[field]]

        return len(missing) == 0, missing


def demo():
    """Demonstration of the parser with example data"""

    example_data = """Model: iPhone 13 128GB Midnight IMEI Number: 356825821305851 Serial Number: Y9WVV62WP9 IMEI2 Number: 356825821314275 MEID Number: 35682582130585 AppleCare Eligible: OFF Estimated Purchase Date: 02/10/21 Carrier: Unlocked Next Tether Policy: 10 Current GSMA Status: Clean Find My iPhone: OFF SimLock: Unlocked"""

    # Fix formatting to have newlines
    example_data_formatted = """Model: iPhone 13 128GB Midnight
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

    print("=" * 60)
    print("IMEI Data Parser Demo")
    print("=" * 60)

    parser = IMEIDataParser()

    # Parse the data
    result = parser.parse(example_data_formatted)

    print("\n✓ Parsed Data (Python object):")
    print(result)

    print("\n✓ As Dictionary (snake_case keys):")
    for key, value in result.to_dict().items():
        print(f"  {key}: {value}")

    print("\n✓ As Display Dictionary (Human-readable keys):")
    for key, value in result.to_display_dict().items():
        print(f"  {key}: {value}")

    print("\n✓ Headers Found:")
    headers = parser.extract_headers(example_data_formatted)
    for header in headers:
        print(f"  - {header}")

    print("\n✓ Validation:")
    is_valid, missing = parser.validate(example_data_formatted)
    if is_valid:
        print("  ✓ All required fields present")
    else:
        print(f"  ✗ Missing required fields: {', '.join(missing)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
