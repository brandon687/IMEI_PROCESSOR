#!/usr/bin/env python3
"""
Test if we can log in and potentially scrape the API key
"""
import requests
from requests.sessions import Session

# Your login credentials
username = 'scalmobile'
password = 'SCal5566'

base_url = 'https://hammerfusion.com'

print("Attempting to log into hammerfusion.com...")
print("="*80)

session = Session()

# Try to get the login page first
try:
    login_page = session.get(f'{base_url}/', timeout=10)
    print(f"Login page status: {login_page.status_code}")

    # Try common login endpoints
    login_urls = [
        f'{base_url}/login.php',
        f'{base_url}/login',
        f'{base_url}/account/login',
        f'{base_url}/user/login',
        f'{base_url}/index.php?action=login',
    ]

    for url in login_urls:
        print(f"\nTrying login URL: {url}")
        try:
            response = session.post(url, data={
                'username': username,
                'password': password,
                'email': username,
                'user': username,
            }, timeout=10)
            print(f"  Status: {response.status_code}")

            # Check if we're logged in
            if 'api' in response.text.lower() and 'key' in response.text.lower():
                print(f"  Found 'api' and 'key' in response!")

                # Look for API key pattern
                import re
                api_key_pattern = r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'
                matches = re.findall(api_key_pattern, response.text)
                if matches:
                    print(f"\n  FOUND API KEY(S): {matches}")

        except Exception as e:
            print(f"  Error: {e}")

    # Try to access API settings page directly
    print(f"\nTrying direct access to API settings...")
    api_pages = [
        f'{base_url}/api_settings.php',
        f'{base_url}/apisettings.php',
        f'{base_url}/account/api',
        f'{base_url}/settings/api',
    ]

    for url in api_pages:
        print(f"\nTrying: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                import re
                api_key_pattern = r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'
                matches = re.findall(api_key_pattern, response.text)
                if matches:
                    print(f"  FOUND API KEY(S): {matches}")
        except Exception as e:
            print(f"  Error: {e}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("\nNEXT STEPS:")
print("1. Go to https://hammerfusion.com and log in manually")
print(f"   Username: {username}")
print(f"   Password: {password}")
print("2. Look for 'API Settings' or 'API Key' in the menu")
print("3. Copy your actual API key")
print("4. Provide it to me so I can update the .env file")
