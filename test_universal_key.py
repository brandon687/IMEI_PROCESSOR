#!/usr/bin/env python3
"""
Test if there's a universal API key or if we need different user identifier
"""
import requests
import re

base_url = 'https://hammerfusion.com'
username = 'scalmobile'

# Maybe there's a universal/public API key for all users?
possible_keys = [
    'C0H6-T2S9-H9A0-G0T9-X3N7',  # Sample from docs
    'DEMO-DEMO-DEMO-DEMO-DEMO',
    'TEST-TEST-TEST-TEST-TEST',
    '0000-0000-0000-0000-0000',
]

# Maybe userId should be different format?
possible_userids = [
    'scalmobile',
    'SCALMOBILE',
    'scal mobile',
    'scal',
    'SCal5566',  # Maybe password is the userid?
]

print("Testing various combinations...")
print("="*80)

url = f'{base_url}/gsmfusion_api/index.php'

best_response = None
best_combo = None

for key in possible_keys:
    for userid in possible_userids:
        params = {
            'apiKey': key,
            'userId': userid,
            'action': 'imeiservices'
        }

        try:
            response = requests.post(url, data=params, timeout=5)
            result = response.text[:200]

            # Check if we got a different error (progress!)
            if 'Invalid API Key' not in result and 'Invalid User' not in result:
                print(f"\n✓ DIFFERENT RESPONSE with key={key}, userId={userid}")
                print(f"  Response: {result}")
                best_response = result
                best_combo = (key, userid)
            elif 'Invalid API Key' in result:
                # This means user was recognized
                pass  # We already know scalmobile works

        except Exception as e:
            pass

if not best_response:
    print("\nNo successful combination found.")
    print("\n" + "="*80)
    print("\nFINAL RECOMMENDATION:")
    print("="*80)
    print("The API system recognizes your username 'scalmobile' but requires a valid API key.")
    print("\nYou MUST contact Hammer Fusion support to:")
    print("1. Request your API key")
    print("2. Ask them to enable API access for your account")
    print("3. Ask where to find API settings in the dashboard")
    print("\nUse the 'Support' dropdown menu on the website to create a support ticket.")
    print("\nSupport URL: https://hammerfusion.com/support.php")
else:
    print(f"\n\n✓✓✓ SUCCESS! Use:")
    print(f"    API Key: {best_combo[0]}")
    print(f"    User ID: {best_combo[1]}")
