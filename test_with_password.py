#!/usr/bin/env python3
"""
Test if we need to use password instead of API key, or different parameter names
"""
import requests

username = 'scalmobile'
password = 'SCal5566'
api_key_sample = 'C0H6-T2S9-H9A0-G0T9-X3N7'

url = 'https://hammerfusion.com/gsmfusion_api/index.php'

print("Testing different authentication methods...")
print("="*80)

# Test 1: Original method with HTTPS
print("\n1. Testing with sample API key + HTTPS:")
params = {
    'apiKey': api_key_sample,
    'userId': username,
    'action': 'imeiservices'
}
response = requests.post(url, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 2: Maybe password is needed instead of API key?
print("\n2. Testing with password instead of API key:")
params = {
    'apiKey': password,
    'userId': username,
    'action': 'imeiservices'
}
response = requests.post(url, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 3: Maybe both are needed?
print("\n3. Testing with both API key and password:")
params = {
    'apiKey': api_key_sample,
    'userId': username,
    'password': password,
    'action': 'imeiservices'
}
response = requests.post(url, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 4: Different parameter names
print("\n4. Testing with different parameter names (username/password):")
params = {
    'username': username,
    'password': password,
    'action': 'imeiservices'
}
response = requests.post(url, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 5: Email instead of username?
print("\n5. Testing if username should be email format:")
params = {
    'apiKey': api_key_sample,
    'userId': f'{username}@scalmobile.com',
    'action': 'imeiservices'
}
response = requests.post(url, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 6: Check what the newer API endpoint wants
print("\n6. Testing newer API endpoint at /api/:")
url2 = 'https://hammerfusion.com/api/index.php'
params = {
    'apiKey': api_key_sample,
    'userId': username,
    'action': 'imeiservices'
}
response = requests.post(url2, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

# Test 7: With password on newer API
print("\n7. Testing newer API with password:")
params = {
    'username': username,
    'password': password,
    'action': 'imeiservices'
}
response = requests.post(url2, data=params, timeout=10)
print(f"   Response: {response.text[:200]}")

print("\n" + "="*80)
