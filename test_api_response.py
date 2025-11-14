#!/usr/bin/env python3
"""
Quick test to see actual API response
"""
import os
import requests

api_key = os.getenv('GSM_FUSION_API_KEY')
username = os.getenv('GSM_FUSION_USERNAME')
base_url = os.getenv('GSM_FUSION_BASE_URL')

url = f"{base_url}/gsmfusion_api/index.php"

parameters = {
    'apiKey': api_key,
    'userId': username,
    'action': 'imeiservices'
}

print("Making request to:", url)
print("Parameters:", {k: v for k, v in parameters.items() if k != 'apiKey'})
print("\n" + "="*80)

response = requests.post(url, data=parameters, timeout=30)

print("Status Code:", response.status_code)
print("\n" + "="*80)
print("Response Content:")
print("="*80)
print(response.text[:2000])  # Print first 2000 characters
print("\n" + "="*80)
