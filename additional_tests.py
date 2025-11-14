#!/usr/bin/env python3
"""
Additional specific tests based on findings
"""

import requests
import json

USERNAME = "scalmobile"
API_KEY = "C0H6-T2S9-H9A0-G0T9-X3N7"

print("="*80)
print("ADDITIONAL FOCUSED TESTS")
print("="*80)

# Test 1: Check if ANY username works (test if username recognition is real)
print("\n1. Testing with a completely fake username:")
response = requests.post(
    "https://hammerfusion.com/gsmfusion_api/index.php",
    data={
        'username': 'totally_fake_user_12345',
        'api_key': API_KEY,
        'action': 'getServerList'
    }
)
print(f"Response: {response.text}")

# Test 2: Test without any credentials
print("\n2. Testing without any credentials:")
response = requests.post(
    "https://hammerfusion.com/gsmfusion_api/index.php",
    data={
        'action': 'getServerList'
    }
)
print(f"Response: {response.text}")

# Test 3: Test root API without any parameters
print("\n3. Testing API root without parameters:")
response = requests.get("https://hammerfusion.com/gsmfusion_api/index.php")
print(f"Response: {response.text}")

# Test 4: Test /api/ endpoint for version info
print("\n4. Testing /api/ for version info:")
response = requests.get("https://hammerfusion.com/api/index.php")
print(f"Response: {response.text}")

# Test 5: Try to find documentation
print("\n5. Testing for API documentation endpoints:")
endpoints = [
    "https://hammerfusion.com/api/docs",
    "https://hammerfusion.com/api/help",
    "https://hammerfusion.com/gsmfusion_api/docs",
    "https://hammerfusion.com/gsmfusion_api/help.php",
]
for endpoint in endpoints:
    response = requests.get(endpoint)
    print(f"\n{endpoint}: Status {response.status_code}")
    if response.status_code == 200:
        print(f"Content: {response.text[:200]}")

# Test 6: Check if the error message changes with just username
print("\n6. Testing with only username (no API key):")
response = requests.post(
    "https://hammerfusion.com/gsmfusion_api/index.php",
    data={
        'username': USERNAME,
        'action': 'getServerList'
    }
)
print(f"Response: {response.text}")

# Test 7: Test with empty API key
print("\n7. Testing with empty API key:")
response = requests.post(
    "https://hammerfusion.com/gsmfusion_api/index.php",
    data={
        'username': USERNAME,
        'api_key': '',
        'action': 'getServerList'
    }
)
print(f"Response: {response.text}")

# Test 8: Test OPTIONS method to see allowed methods
print("\n8. Testing OPTIONS method:")
response = requests.options("https://hammerfusion.com/gsmfusion_api/index.php")
print(f"Status: {response.status_code}")
print(f"Allow header: {response.headers.get('Allow', 'Not present')}")
print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not present')}")

# Test 9: Check robots.txt
print("\n9. Checking robots.txt:")
response = requests.get("https://hammerfusion.com/robots.txt")
if response.status_code == 200:
    print(f"robots.txt found:\n{response.text}")

# Test 10: Check for API in different path
print("\n10. Testing alternative paths:")
alt_paths = [
    "https://hammerfusion.com/api.php",
    "https://hammerfusion.com/gsmfusion.php",
    "https://hammerfusion.com/fusion_api/index.php",
]
for path in alt_paths:
    try:
        response = requests.get(path, timeout=5)
        print(f"{path}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Content: {response.text[:100]}")
    except Exception as e:
        print(f"{path}: {str(e)}")

# Test 11: Try common API actions that might not require auth
print("\n11. Testing common public API actions:")
public_actions = ['version', 'ping', 'status', 'health', 'test']
for action in public_actions:
    response = requests.post(
        "https://hammerfusion.com/gsmfusion_api/index.php",
        data={'action': action}
    )
    if response.text != "<?phpxml version=\"1.0\" encoding=\"utf-8\"?><error>Invalid User!</error>":
        print(f"Action '{action}': {response.text}")

# Test 12: Try JSON API with different parameters
print("\n12. Testing JSON API (/api/) with various parameters:")
response = requests.post(
    "https://hammerfusion.com/api/index.php",
    json={
        'username': USERNAME,
        'api_key': API_KEY,
        'action': 'getServerList'
    },
    headers={'Content-Type': 'application/json'}
)
print(f"JSON API response: {response.text}")

# Test 13: Check if there's an API version endpoint
print("\n13. Checking for API version endpoint:")
response = requests.post(
    "https://hammerfusion.com/api/index.php",
    data={'action': 'version'}
)
print(f"Response: {response.text}")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("""
Based on all tests:
1. All authentication attempts return 'Invalid User!' error
2. The XML endpoint has a PHP parsing issue (<?phpxml instead of <?xml)
3. The JSON API endpoint (/api/) properly returns JSON with API version 2.0.0
4. Both endpoints consistently reject the provided credentials
5. The username 'scalmobile' may or may not be valid (need to test)
6. The API key 'C0H6-T2S9-H9A0-G0T9-X3N7' appears to be sample/dummy data
""")

print("\nRECOMMENDATIONS:")
print("-" * 80)
print("1. The API key from docs is likely a PLACEHOLDER, not a real key")
print("2. You need to contact Hammer Fusion support to get a real API key")
print("3. The username 'scalmobile' needs to be verified as valid")
print("4. Consider looking for registration/account creation endpoints")
print("5. Check if there's a web portal where you can generate API keys")
