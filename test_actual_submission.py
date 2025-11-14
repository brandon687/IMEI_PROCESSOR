#!/usr/bin/env python3
"""Test with the IMEI that worked on the website"""

from dotenv import load_dotenv
from gsm_fusion_client import GSMFusionClient

load_dotenv()

try:
    client = GSMFusionClient()

    print("Testing order placement...")
    print("IMEI: 353370080089458")
    print("Service ID: 1739")
    print()

    # Make raw request first
    parameters = {
        'imei': "353370080089458",
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
    data = client._parse_xml_response(xml_response)
    print(f"Type: {type(data)}")
    print(f"Content: {data}")
    print()

    # Now try the full method
    print("=" * 80)
    print("USING place_imei_order METHOD:")
    print("=" * 80)
    result = client.place_imei_order(
        imei="353370080089458",
        network_id="1739"
    )

    print(f"Orders: {result['orders']}")
    print(f"Duplicates: {result['duplicates']}")
    print(f"Errors: {result['errors']}")

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
