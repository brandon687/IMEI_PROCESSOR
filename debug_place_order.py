#!/usr/bin/env python3
"""Debug order placement - see raw response"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient

load_dotenv()

try:
    client = GSMFusionClient()

    print("Testing order placement...")
    print("IMEI: 353990097369512")
    print("Service ID: 1739")
    print()

    # Make raw request
    parameters = {
        'imei': "353990097369512",
        'networkId': "1739"
    }

    xml_response = client._make_request('placeorder', parameters)

    print("=" * 80)
    print("RAW XML RESPONSE:")
    print("=" * 80)
    print(xml_response)
    print()

    print("=" * 80)
    print("PARSED RESPONSE:")
    print("=" * 80)
    try:
        data = client._parse_xml_response(xml_response)
        print(f"Type: {type(data)}")
        print(f"Content: {data}")
    except Exception as e:
        print(f"Parse error: {e}")

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
