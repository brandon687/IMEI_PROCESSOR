#!/usr/bin/env python3
"""
ABSOLUTE FINAL VERIFICATION - Test API key one more time with extreme precision
"""
import requests
import json
from datetime import datetime

# The credentials in question
API_KEY = 'C0H6-T2S9-H9A0-G0T9-X3N7'
USERNAME = 'scalmobile'

print("="*80)
print("ABSOLUTE FINAL VERIFICATION TEST")
print("="*80)
print(f"Testing API Key: {API_KEY}")
print(f"Testing Username: {USERNAME}")
print(f"Timestamp: {datetime.now()}")
print("="*80)

# Test 1: Exact original configuration - HTTPS
print("\n[TEST 1] HTTPS endpoint with exact parameters from docs:")
url = 'https://hammerfusion.com/gsmfusion_api/index.php'
params = {
    'apiKey': API_KEY,
    'userId': USERNAME,
    'action': 'imeiservices'
}
try:
    response = requests.post(url, data=params, timeout=10)
    print(f"  URL: {url}")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.text}")

    # Check if successful
    if 'Package' in response.text or 'Packages' in response.text:
        print("\n  ✓✓✓ SUCCESS! API key works!")
        success = True
    elif 'Invalid API Key' in response.text:
        print("\n  ✗ FAILED: Invalid API Key error")
        success = False
    elif 'Invalid User' in response.text:
        print("\n  ✗ FAILED: Invalid User error")
        success = False
    else:
        print("\n  ? UNKNOWN RESPONSE")
        success = False
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    success = False

# Test 2: HTTP endpoint (from PDF docs)
print("\n[TEST 2] HTTP endpoint (as mentioned in PDF):")
url = 'http://hammerfusion.com/gsmfusion_api/index.php'
params = {
    'apiKey': API_KEY,
    'userId': USERNAME,
    'action': 'imeiservices'
}
try:
    response = requests.post(url, data=params, timeout=10)
    print(f"  URL: {url}")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.text}")

    if 'Package' in response.text or 'Packages' in response.text:
        print("\n  ✓✓✓ SUCCESS! API key works!")
        success = True
    elif 'Invalid API Key' in response.text:
        print("\n  ✗ FAILED: Invalid API Key error")
    elif 'Invalid User' in response.text:
        print("\n  ✗ FAILED: Invalid User error")
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 3: Alternative JSON API endpoint
print("\n[TEST 3] JSON API endpoint:")
url = 'https://hammerfusion.com/api/index.php'
params = {
    'apiKey': API_KEY,
    'userId': USERNAME,
    'action': 'imeiservices'
}
try:
    response = requests.post(url, data=params, timeout=10)
    print(f"  URL: {url}")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.text}")

    # Try to parse as JSON
    try:
        json_data = json.loads(response.text)
        if 'ERROR' in json_data:
            print(f"\n  ✗ FAILED: {json_data['ERROR']}")
        elif 'Package' in json_data or 'Packages' in json_data:
            print("\n  ✓✓✓ SUCCESS! API key works!")
            success = True
    except:
        if 'Package' in response.text:
            print("\n  ✓✓✓ SUCCESS! API key works!")
            success = True
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 4: Simple connectivity test - can we even reach the service?
print("\n[TEST 4] Basic service connectivity:")
url = 'https://hammerfusion.com/gsmfusion_api/index.php'
try:
    response = requests.post(url, data={'action': 'imeiservices'}, timeout=10)
    print(f"  Service is reachable: YES")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response snippet: {response.text[:100]}")
except Exception as e:
    print(f"  Service is reachable: NO")
    print(f"  Error: {e}")

print("\n" + "="*80)
print("FINAL VERDICT:")
print("="*80)

if success:
    print("✓ API KEY WORKS!")
    print(f"  API Key: {API_KEY}")
    print(f"  Username: {USERNAME}")
    print("\nYou can proceed with using this configuration.")
else:
    print("✗ API KEY DOES NOT WORK")
    print(f"  Tested API Key: {API_KEY}")
    print(f"  Tested Username: {USERNAME}")
    print("\nThis is a placeholder/sample key from documentation.")
    print("\nREQUIRED ACTIONS:")
    print("1. Check the Gmail email that contained these files")
    print("2. Look for actual API credentials in the email body")
    print("3. Contact Hammer Fusion support to request your real API key")
    print("4. URL: https://hammerfusion.com/ticket.php")

print("="*80)
