#!/usr/bin/env python3
"""Debug script to see what the API returns"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient

load_dotenv()

try:
    client = GSMFusionClient()

    # Make raw request
    xml_response = client._make_request('imeiservices')

    print("=" * 80)
    print("RAW XML RESPONSE:")
    print("=" * 80)
    print(xml_response)
    print("\n")

    print("=" * 80)
    print("PARSED RESPONSE:")
    print("=" * 80)
    try:
        data = client._parse_xml_response(xml_response)
        print(f"Type: {type(data)}")
        print(f"Data keys: {data.keys() if isinstance(data, dict) else 'N/A'}")

        # Check if packages are directly under root
        if isinstance(data, dict):
            if 'Package' in data:
                packages = data['Package']
                if isinstance(packages, list):
                    print(f"\nFound {len(packages)} packages directly under root")
                    print(f"First package: {packages[0]}")
                else:
                    print(f"\nFound 1 package directly under root")
                    print(f"Package: {packages}")
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
