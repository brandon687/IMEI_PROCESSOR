#!/usr/bin/env python3
"""
Final critical tests to determine if username matters at all
"""

import requests

print("="*80)
print("CRITICAL TEST: Does the username even matter?")
print("="*80)

test_cases = [
    ("Real username from docs", "scalmobile", "C0H6-T2S9-H9A0-G0T9-X3N7"),
    ("Fake username #1", "fake_user_xyz", "C0H6-T2S9-H9A0-G0T9-X3N7"),
    ("Empty username", "", "C0H6-T2S9-H9A0-G0T9-X3N7"),
    ("Admin username", "admin", "C0H6-T2S9-H9A0-G0T9-X3N7"),
    ("Test username", "test", "C0H6-T2S9-H9A0-G0T9-X3N7"),
    ("No username at all", None, "C0H6-T2S9-H9A0-G0T9-X3N7"),
]

print("\nTesting XML API (gsmfusion_api):")
print("-"*80)
for name, username, api_key in test_cases:
    params = {'action': 'getServerList', 'api_key': api_key}
    if username is not None:
        params['username'] = username

    response = requests.post(
        "https://hammerfusion.com/gsmfusion_api/index.php",
        data=params
    )
    print(f"{name:30} -> {response.text}")

print("\n\nTesting JSON API (/api/):")
print("-"*80)
for name, username, api_key in test_cases:
    params = {'action': 'getServerList', 'api_key': api_key}
    if username is not None:
        params['username'] = username

    response = requests.post(
        "https://hammerfusion.com/api/index.php",
        data=params
    )
    print(f"{name:30} -> {response.text}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("""
If all responses are IDENTICAL regardless of username, then:
1. The API is NOT actually checking the username
2. The "Invalid User!" message is a generic catch-all error
3. Either the API requires additional setup/activation
4. Or the endpoints are intentionally returning errors

Next steps would be to:
- Check if there's a web portal to activate the API
- Contact support for proper credentials
- Look for account registration endpoints
""")
