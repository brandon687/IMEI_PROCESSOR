#!/usr/bin/env python3
"""
Try to find or generate API key through various methods
"""
import requests
from bs4 import BeautifulSoup

username = 'scalmobile'
password = 'SCal5566'
base_url = 'https://hammerfusion.com'

print("Attempting to find/generate API key...")
print("="*80)

# Create session and try to login
session = requests.Session()

# Common login form fields
login_data_variants = [
    {'username': username, 'password': password},
    {'email': username, 'password': password},
    {'user': username, 'pass': password},
    {'login': username, 'password': password},
]

# Try to find login endpoint
print("\n1. Attempting login...")
login_response = session.post(f'{base_url}/login.php', data=login_data_variants[0], timeout=10)
print(f"   Login status: {login_response.status_code}")

# Now try to access various pages that might have API settings
pages_to_check = [
    '/myprofile.php',
    '/profile.php',
    '/api_settings.php',
    '/api.php',
    '/settings.php',
    '/account.php',
    '/developer.php',
    '/integration.php',
    '/api_key.php',
    '/generate_api_key.php',
]

print("\n2. Checking for API-related pages...")
for page in pages_to_check:
    try:
        response = session.get(f'{base_url}{page}', timeout=10)
        if response.status_code == 200:
            # Look for API key pattern in response
            import re
            api_pattern = r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'
            matches = re.findall(api_pattern, response.text)

            if matches:
                print(f"\n   ✓ FOUND on {page}:")
                for match in matches:
                    if match != 'C0H6-T2S9-H9A0-G0T9-X3N7':  # Ignore sample key
                        print(f"     API KEY: {match}")

            # Check if page mentions API
            if 'api key' in response.text.lower() or 'api_key' in response.text.lower():
                print(f"   → {page} mentions API key")

    except Exception as e:
        pass

print("\n3. Checking if API needs to be enabled via support...")
# Check support/documentation pages
support_pages = [
    '/support.php',
    '/help.php',
    '/faq.php',
    '/documentation.php',
    '/api_documentation.php',
]

for page in support_pages:
    try:
        response = session.get(f'{base_url}{page}', timeout=10)
        if response.status_code == 200 and 'api' in response.text.lower():
            print(f"   → {page} has API information")
    except:
        pass

print("\n" + "="*80)
print("\nRECOMMENDATIONS:")
print("1. Contact Hammer Fusion support through the 'Support' menu")
print("2. Ask them to provide or enable your API key")
print("3. Or ask them how to access API settings for your account")
print("\nAlternatively, try opening these URLs directly in your browser while logged in:")
print("   https://hammerfusion.com/api_settings.php")
print("   https://hammerfusion.com/myprofile.php")
