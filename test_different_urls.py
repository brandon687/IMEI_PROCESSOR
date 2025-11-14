#!/usr/bin/env python3
"""
Test different possible URLs and configurations
"""
import os
import requests

api_key = 'C0H6-T2S9-H9A0-G0T9-X3N7'
username = 'scalmobile'

# Possible URLs to try
urls = [
    'http://hammerfusion.com/gsmfusion_api/index.php',
    'https://hammerfusion.com/gsmfusion_api/index.php',
    'http://www.hammerfusion.com/gsmfusion_api/index.php',
    'https://www.hammerfusion.com/gsmfusion_api/index.php',
    'http://hammerfusion.com/api/index.php',
    'http://hammerfusion.com/index.php',
]

parameters = {
    'apiKey': api_key,
    'userId': username,
    'action': 'imeiservices'
}

print("Testing different URL configurations...")
print("="*80)

for url in urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.post(url, data=parameters, timeout=10)
        print(f"  Status: {response.status_code}")

        # Show first 500 chars of response
        content = response.text[:500]
        if 'error' in content.lower():
            print(f"  Response: {content}")
        elif 'Package' in content or 'Packages' in content:
            print(f"  SUCCESS! Found service data")
            print(f"  Response preview: {content[:200]}...")
            break
        else:
            print(f"  Response: {content}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
