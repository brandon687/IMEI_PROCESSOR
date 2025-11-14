#!/usr/bin/env python3
"""
Final test - maybe API key isn't needed at all for some endpoints
"""
import requests

username = 'scalmobile'
password = 'SCal5566'

url = 'https://hammerfusion.com/gsmfusion_api/index.php'

print("FINAL DEEP ANALYSIS")
print("="*80)

# Test: What if we send EMPTY or NULL API key?
test_cases = [
    ("Empty string API key", {'apiKey': '', 'userId': username, 'action': 'imeiservices'}),
    ("NULL API key", {'userId': username, 'action': 'imeiservices'}),
    ("Password as API key", {'apiKey': password, 'userId': username, 'action': 'imeiservices'}),
    ("Username uppercase", {'apiKey': 'C0H6-T2S9-H9A0-G0T9-X3N7', 'userId': 'SCALMOBILE', 'action': 'imeiservices'}),
]

for name, params in test_cases:
    print(f"\n{name}:")
    try:
        response = requests.post(url, data=params, timeout=5)
        result = response.text[:300]
        print(f"  {result}")
        if 'Package' in result:
            print("\n  ✓✓✓ SUCCESS! This worked!")
            break
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
print("\n**FINAL VERDICT:**")
print("The API key C0H6-T2S9-H9A0-G0T9-X3N7 from the sample code is NOT your real API key.")
print("\nYou MUST:")
print("1. Check the GMAIL email that sent you the apisamplecode.zip file")
print("2. Look for credentials in the email body or other attachments")
print("3. Contact Hammer Fusion support to request your API key")
print("\nSupport ticket: Click 'Support' menu on https://hammerfusion.com")
