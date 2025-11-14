#!/usr/bin/env python3
"""
Try to find the API key page by testing common URLs
"""
import requests

# Possible API settings page URLs
urls = [
    'https://hammerfusion.com/api_settings.php',
    'https://hammerfusion.com/apisettings.php',
    'https://hammerfusion.com/api-settings.php',
    'https://hammerfusion.com/settings/api',
    'https://hammerfusion.com/account/api',
    'https://hammerfusion.com/myapi.php',
    'https://hammerfusion.com/api.php',
    'https://hammerfusion.com/apikey.php',
    'https://hammerfusion.com/api_key.php',
    'https://hammerfusion.com/developer.php',
    'https://hammerfusion.com/integration.php',
]

print("Searching for API Settings page...")
print("="*80)

for url in urls:
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            content = response.text.lower()
            if 'api' in content and ('key' in content or 'settings' in content):
                print(f"\n✓ FOUND: {url}")
                print(f"  Status: {response.status_code}")
                print(f"  Final URL: {response.url}")

                # Look for login requirement
                if 'login' in content or 'sign in' in content:
                    print("  Note: Requires login")
                else:
                    print("  Note: May be accessible")
            else:
                print(f"  {url} - Exists but may not be API page")
        elif response.status_code == 302 or response.status_code == 301:
            print(f"  {url} - Redirects to: {response.headers.get('Location', 'unknown')}")
    except requests.exceptions.RequestException:
        pass

print("\n" + "="*80)
print("\nPlease manually check the 'Other' dropdown menu on the website!")
