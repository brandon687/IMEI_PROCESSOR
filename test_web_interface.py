#!/usr/bin/env python3
"""
Web Interface Test Suite
Tests all endpoints and functionality
"""

import requests
import time
import sys

BASE_URL = "http://localhost:5001"

def test_endpoint(name, url, expected_text=None):
    """Test an endpoint"""
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"

        if expected_text and response.status_code == 200:
            if expected_text in response.text:
                content_check = "✅"
            else:
                content_check = "❌"
                status = "⚠️"
        else:
            content_check = ""

        print(f"{status} {content_check} {name:30s} - {response.status_code} - {url}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌    {name:30s} - CONNECTION REFUSED - {url}")
        return False
    except Exception as e:
        print(f"❌    {name:30s} - ERROR: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("GSM FUSION WEB INTERFACE - TEST SUITE")
    print("=" * 80)
    print()

    # Check if server is running
    print("🔍 Checking if server is running...")
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Server is responding!")
        print()
    except:
        print("❌ Server is NOT running!")
        print()
        print("To start the server:")
        print("  cd /Users/brandonin/Desktop/HAMMER-API")
        print("  python3 web_app.py")
        print()
        sys.exit(1)

    # Test all endpoints
    print("📋 Testing Endpoints:")
    print("-" * 80)

    results = []

    results.append(test_endpoint(
        "Home Page",
        f"{BASE_URL}/",
        "GSM Fusion API Tester"
    ))

    results.append(test_endpoint(
        "All Services",
        f"{BASE_URL}/services",
        "All Services"
    ))

    results.append(test_endpoint(
        "Submit Order Form",
        f"{BASE_URL}/submit",
        "Submit New Order"
    ))

    results.append(test_endpoint(
        "Order History",
        f"{BASE_URL}/history",
        "Order History"
    ))

    # Test with specific service
    results.append(test_endpoint(
        "Service Detail (1739)",
        f"{BASE_URL}/service/1739",
        "Service Details"
    ))

    # Test API endpoint
    print()
    print("🔧 Testing API Client:")
    print("-" * 80)

    try:
        from gsm_fusion_client import GSMFusionClient
        client = GSMFusionClient()
        services = client.get_imei_services()
        client.close()

        if len(services) > 0:
            print(f"✅ API Client Working      - Retrieved {len(services)} services")
            results.append(True)
        else:
            print(f"⚠️ API Client Warning      - No services retrieved")
            results.append(False)
    except Exception as e:
        print(f"❌ API Client Failed       - {str(e)}")
        results.append(False)

    # Summary
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print()
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your web interface is working perfectly!")
        print()
        print("Open your browser and navigate to:")
        print(f"   {BASE_URL}")
        print()
    else:
        print()
        print("⚠️ SOME TESTS FAILED")
        print()
        print("Common issues:")
        print("  1. Server not running - Run: python3 web_app.py")
        print("  2. Wrong port - Check if using port 5001")
        print("  3. API credentials - Check .env file")
        print()

    print("=" * 80)

if __name__ == "__main__":
    main()
