#!/usr/bin/env python3
"""
Comprehensive Hammer Fusion API Authentication Test Suite
Tests every possible authentication variation to determine if API key is valid
"""

import requests
import json
import base64
import urllib.parse
import hashlib
import hmac
import time
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

# Configuration
USERNAME = "scalmobile"
API_KEY = "C0H6-T2S9-H9A0-G0T9-X3N7"
ENDPOINTS = [
    "https://hammerfusion.com/gsmfusion_api/index.php",
    "https://hammerfusion.com/api/index.php",
    "https://hammerfusion.com/gsmfusion_api/",
    "https://hammerfusion.com/api/",
]

class APITester:
    def __init__(self):
        self.results = []
        self.test_number = 0

    def log_result(self, test_name: str, method: str, url: str,
                   params: Dict, headers: Dict, response: requests.Response):
        """Log detailed test results"""
        self.test_number += 1

        result = {
            'test_number': self.test_number,
            'test_name': test_name,
            'method': method,
            'url': url,
            'params': params,
            'headers': headers,
            'status_code': response.status_code,
            'response_text': response.text[:500],  # First 500 chars
            'response_headers': dict(response.headers),
            'cookies': dict(response.cookies),
            'elapsed': response.elapsed.total_seconds()
        }

        self.results.append(result)

        # Print summary
        print(f"\n{'='*80}")
        print(f"TEST #{self.test_number}: {test_name}")
        print(f"{'='*80}")
        print(f"Method: {method}")
        print(f"URL: {url}")
        print(f"Params: {json.dumps(params, indent=2)}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Status: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response Text: {response.text[:500]}")
        print(f"Cookies: {dict(response.cookies)}")

        # Check for interesting responses
        if "Invalid API Key" not in response.text and "Invalid User" not in response.text:
            print(f"\n🎯 INTERESTING RESPONSE DETECTED!")
            print(f"Full response: {response.text}")

        return result

    def make_request(self, test_name: str, method: str, url: str,
                     params: Dict = None, headers: Dict = None,
                     data: Dict = None, json_data: Dict = None):
        """Make HTTP request and log results"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == "POST":
                if json_data:
                    response = requests.post(url, json=json_data, headers=headers, timeout=10)
                else:
                    response = requests.post(url, data=data or params, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, data=data or params, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                print(f"Unsupported method: {method}")
                return None

            return self.log_result(test_name, method, url, params or data or json_data or {},
                                  headers or {}, response)
        except Exception as e:
            print(f"ERROR in {test_name}: {str(e)}")
            return None

    def test_basic_variations(self):
        """Test 1-10: Basic parameter variations"""
        print("\n" + "="*80)
        print("SECTION 1: BASIC PARAMETER VARIATIONS")
        print("="*80)

        base_url = ENDPOINTS[0]

        # Test 1: Original format
        self.make_request(
            "Original format from docs",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 2: Case variations - lowercase key
        self.make_request(
            "Lowercase API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY.lower(),
                'action': 'getServerList'
            }
        )

        # Test 3: Case variations - uppercase key
        self.make_request(
            "Uppercase API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY.upper(),
                'action': 'getServerList'
            }
        )

        # Test 4: Key without dashes
        self.make_request(
            "API key without dashes",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY.replace('-', ''),
                'action': 'getServerList'
            }
        )

        # Test 5: GET method
        self.make_request(
            "GET method with query params",
            "GET",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 6: Different parameter names
        self.make_request(
            "Alternative param: apikey (no underscore)",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'apikey': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 7: Alternative param: key
        self.make_request(
            "Alternative param: key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 8: Alternative param: token
        self.make_request(
            "Alternative param: token",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'token': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 9: URL encoded parameters
        self.make_request(
            "URL encoded API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': urllib.parse.quote(API_KEY),
                'action': 'getServerList'
            }
        )

        # Test 10: Different action
        self.make_request(
            "Different action: checkStatus",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'checkStatus'
            }
        )

    def test_encoding_variations(self):
        """Test 11-20: Different encoding methods"""
        print("\n" + "="*80)
        print("SECTION 2: ENCODING VARIATIONS")
        print("="*80)

        base_url = ENDPOINTS[0]

        # Test 11: Base64 encoded API key
        api_key_b64 = base64.b64encode(API_KEY.encode()).decode()
        self.make_request(
            "Base64 encoded API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': api_key_b64,
                'action': 'getServerList'
            }
        )

        # Test 12: MD5 hash of API key
        api_key_md5 = hashlib.md5(API_KEY.encode()).hexdigest()
        self.make_request(
            "MD5 hashed API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': api_key_md5,
                'action': 'getServerList'
            }
        )

        # Test 13: SHA256 hash of API key
        api_key_sha256 = hashlib.sha256(API_KEY.encode()).hexdigest()
        self.make_request(
            "SHA256 hashed API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': api_key_sha256,
                'action': 'getServerList'
            }
        )

        # Test 14: Combined username:apikey
        combined = f"{USERNAME}:{API_KEY}"
        self.make_request(
            "Combined username:apikey",
            "POST",
            base_url,
            params={
                'credentials': combined,
                'action': 'getServerList'
            }
        )

        # Test 15: Base64 of username:apikey
        combined_b64 = base64.b64encode(combined.encode()).decode()
        self.make_request(
            "Base64 of username:apikey",
            "POST",
            base_url,
            params={
                'credentials': combined_b64,
                'action': 'getServerList'
            }
        )

        # Test 16: HMAC signature (username as key, apikey as message)
        hmac_sig = hmac.new(USERNAME.encode(), API_KEY.encode(), hashlib.sha256).hexdigest()
        self.make_request(
            "HMAC signature",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'signature': hmac_sig,
                'action': 'getServerList'
            }
        )

        # Test 17: Timestamp-based auth
        timestamp = str(int(time.time()))
        self.make_request(
            "With timestamp parameter",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'timestamp': timestamp,
                'action': 'getServerList'
            }
        )

        # Test 18: JSON payload
        self.make_request(
            "JSON payload",
            "POST",
            base_url,
            json_data={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 19: Hex encoded API key
        api_key_hex = API_KEY.encode().hex()
        self.make_request(
            "Hex encoded API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': api_key_hex,
                'action': 'getServerList'
            }
        )

        # Test 20: Double URL encoding
        api_key_double_encoded = urllib.parse.quote(urllib.parse.quote(API_KEY))
        self.make_request(
            "Double URL encoded API key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': api_key_double_encoded,
                'action': 'getServerList'
            }
        )

    def test_header_variations(self):
        """Test 21-30: HTTP header authentication"""
        print("\n" + "="*80)
        print("SECTION 3: HEADER-BASED AUTHENTICATION")
        print("="*80)

        base_url = ENDPOINTS[0]

        # Test 21: API key in Authorization header
        self.make_request(
            "API key in Authorization header",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'action': 'getServerList'
            },
            headers={
                'Authorization': API_KEY
            }
        )

        # Test 22: Bearer token
        self.make_request(
            "Bearer token in Authorization",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'action': 'getServerList'
            },
            headers={
                'Authorization': f'Bearer {API_KEY}'
            }
        )

        # Test 23: Basic auth
        auth_string = base64.b64encode(f"{USERNAME}:{API_KEY}".encode()).decode()
        self.make_request(
            "Basic Authentication",
            "POST",
            base_url,
            params={
                'action': 'getServerList'
            },
            headers={
                'Authorization': f'Basic {auth_string}'
            }
        )

        # Test 24: Custom X-API-Key header
        self.make_request(
            "X-API-Key header",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'action': 'getServerList'
            },
            headers={
                'X-API-Key': API_KEY
            }
        )

        # Test 25: Custom X-Auth-Token header
        self.make_request(
            "X-Auth-Token header",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'action': 'getServerList'
            },
            headers={
                'X-Auth-Token': API_KEY
            }
        )

        # Test 26: API-Key header
        self.make_request(
            "API-Key header",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'action': 'getServerList'
            },
            headers={
                'API-Key': API_KEY
            }
        )

        # Test 27: Combined headers
        self.make_request(
            "Multiple auth headers",
            "POST",
            base_url,
            params={
                'action': 'getServerList'
            },
            headers={
                'X-Username': USERNAME,
                'X-API-Key': API_KEY
            }
        )

        # Test 28: Content-Type variations
        self.make_request(
            "application/x-www-form-urlencoded",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # Test 29: JSON content type
        self.make_request(
            "application/json content type",
            "POST",
            base_url,
            json_data={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            },
            headers={
                'Content-Type': 'application/json'
            }
        )

        # Test 30: XML content type
        self.make_request(
            "application/xml content type",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            },
            headers={
                'Content-Type': 'application/xml'
            }
        )

    def test_alternative_endpoints(self):
        """Test 31-40: Alternative endpoints and paths"""
        print("\n" + "="*80)
        print("SECTION 4: ALTERNATIVE ENDPOINTS")
        print("="*80)

        # Test 31-34: Test all endpoint variations
        for i, endpoint in enumerate(ENDPOINTS):
            self.make_request(
                f"Endpoint variation {i+1}: {endpoint}",
                "POST",
                endpoint,
                params={
                    'username': USERNAME,
                    'api_key': API_KEY,
                    'action': 'getServerList'
                }
            )

        # Test 35: Alternative API endpoint with GET
        self.make_request(
            "Alternative /api/ endpoint with GET",
            "GET",
            ENDPOINTS[1],
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 36: Test without action parameter
        self.make_request(
            "Without action parameter",
            "POST",
            ENDPOINTS[0],
            params={
                'username': USERNAME,
                'api_key': API_KEY
            }
        )

        # Test 37: Test with version parameter
        self.make_request(
            "With version parameter",
            "POST",
            ENDPOINTS[0],
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList',
                'version': '1.0'
            }
        )

        # Test 38: Test with format parameter
        self.make_request(
            "With format=json parameter",
            "POST",
            ENDPOINTS[0],
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList',
                'format': 'json'
            }
        )

        # Test 39: Test with format=xml parameter
        self.make_request(
            "With format=xml parameter",
            "POST",
            ENDPOINTS[0],
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList',
                'format': 'xml'
            }
        )

        # Test 40: PUT method
        self.make_request(
            "PUT method",
            "PUT",
            ENDPOINTS[0],
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

    def test_no_auth_endpoints(self):
        """Test 41-50: Endpoints that might work without authentication"""
        print("\n" + "="*80)
        print("SECTION 5: NO-AUTH / PUBLIC ENDPOINTS")
        print("="*80)

        base_url = ENDPOINTS[0]

        public_actions = [
            'version', 'info', 'status', 'ping', 'health',
            'getVersion', 'getInfo', 'getStatus', 'help', 'docs'
        ]

        for i, action in enumerate(public_actions):
            self.make_request(
                f"Public endpoint: {action}",
                "GET",
                base_url,
                params={
                    'action': action
                }
            )

    def test_advanced_scenarios(self):
        """Test 51-60: Advanced authentication scenarios"""
        print("\n" + "="*80)
        print("SECTION 6: ADVANCED SCENARIOS")
        print("="*80)

        base_url = ENDPOINTS[0]

        # Test 51: Session-based (check if we need to login first)
        self.make_request(
            "Login action with credentials",
            "POST",
            base_url,
            params={
                'action': 'login',
                'username': USERNAME,
                'api_key': API_KEY
            }
        )

        # Test 52: Authenticate action
        self.make_request(
            "Authenticate action",
            "POST",
            base_url,
            params={
                'action': 'authenticate',
                'username': USERNAME,
                'api_key': API_KEY
            }
        )

        # Test 53: Test with password instead of api_key
        self.make_request(
            "Password parameter instead of api_key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'password': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 54: Test with both password and api_key
        self.make_request(
            "Both password and api_key",
            "POST",
            base_url,
            params={
                'username': USERNAME,
                'password': API_KEY,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 55: Different case for username
        self.make_request(
            "Uppercase username",
            "POST",
            base_url,
            params={
                'username': USERNAME.upper(),
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 56: User parameter instead of username
        self.make_request(
            "User parameter instead of username",
            "POST",
            base_url,
            params={
                'user': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 57: Test with client_id
        self.make_request(
            "client_id parameter",
            "POST",
            base_url,
            params={
                'client_id': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 58: OAuth-style parameters
        self.make_request(
            "OAuth-style parameters",
            "POST",
            base_url,
            params={
                'client_id': USERNAME,
                'client_secret': API_KEY,
                'grant_type': 'client_credentials',
                'action': 'getServerList'
            }
        )

        # Test 59: Test root path
        self.make_request(
            "Root path without index.php",
            "POST",
            "https://hammerfusion.com/gsmfusion_api/",
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

        # Test 60: Test with HTTP instead of HTTPS
        self.make_request(
            "HTTP instead of HTTPS",
            "POST",
            "http://hammerfusion.com/gsmfusion_api/index.php",
            params={
                'username': USERNAME,
                'api_key': API_KEY,
                'action': 'getServerList'
            }
        )

    def analyze_results(self):
        """Analyze all test results and provide comprehensive report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE ANALYSIS")
        print("="*80)

        # Group results by response type
        by_response = {}
        for result in self.results:
            if result:
                response_key = result['response_text'][:100]  # First 100 chars as key
                if response_key not in by_response:
                    by_response[response_key] = []
                by_response[response_key].append(result)

        print(f"\nTotal tests performed: {len(self.results)}")
        print(f"\nUnique response types: {len(by_response)}")

        print("\n" + "-"*80)
        print("RESPONSE TYPE ANALYSIS:")
        print("-"*80)

        for i, (response_snippet, tests) in enumerate(by_response.items(), 1):
            print(f"\n{i}. Response type ({len(tests)} tests):")
            print(f"   Response: {response_snippet}...")
            print(f"   Tests that produced this:")
            for test in tests[:3]:  # Show first 3
                print(f"   - Test #{test['test_number']}: {test['test_name']}")
            if len(tests) > 3:
                print(f"   ... and {len(tests) - 3} more")

        # Find interesting responses
        interesting = [r for r in self.results if r and
                      "Invalid API Key" not in r['response_text'] and
                      "Invalid User" not in r['response_text']]

        print("\n" + "-"*80)
        print("INTERESTING RESPONSES (not 'Invalid API Key' or 'Invalid User'):")
        print("-"*80)

        if interesting:
            for result in interesting:
                print(f"\nTest #{result['test_number']}: {result['test_name']}")
                print(f"Method: {result['method']}")
                print(f"URL: {result['url']}")
                print(f"Status: {result['status_code']}")
                print(f"Response: {result['response_text']}")
                print(f"Headers: {json.dumps(result['response_headers'], indent=2)}")
        else:
            print("\nNo interesting responses found. All tests returned expected error messages.")

        # Check status codes
        status_codes = {}
        for result in self.results:
            if result:
                code = result['status_code']
                if code not in status_codes:
                    status_codes[code] = []
                status_codes[code].append(result)

        print("\n" + "-"*80)
        print("STATUS CODE DISTRIBUTION:")
        print("-"*80)
        for code, tests in sorted(status_codes.items()):
            print(f"Status {code}: {len(tests)} tests")

        # Check response headers for clues
        print("\n" + "-"*80)
        print("RESPONSE HEADER ANALYSIS:")
        print("-"*80)

        all_headers = set()
        for result in self.results:
            if result:
                all_headers.update(result['response_headers'].keys())

        print(f"Unique headers seen: {', '.join(sorted(all_headers))}")

        # Look for authentication-related headers
        auth_headers = [h for h in all_headers if
                       'auth' in h.lower() or
                       'token' in h.lower() or
                       'key' in h.lower() or
                       'www-authenticate' in h.lower()]

        if auth_headers:
            print(f"\nAuthentication-related headers found: {', '.join(auth_headers)}")
            for result in self.results:
                if result:
                    for header in auth_headers:
                        if header in result['response_headers']:
                            print(f"Test #{result['test_number']}: {header} = {result['response_headers'][header]}")
        else:
            print("\nNo authentication-related headers found in responses.")

        # Save detailed results to JSON
        with open('/Users/brandonin/Desktop/HAMMER-API/test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n\nDetailed results saved to: /Users/brandonin/Desktop/HAMMER-API/test_results.json")

        return interesting, by_response, status_codes

    def run_all_tests(self):
        """Execute all test suites"""
        print("\n" + "="*80)
        print("HAMMER FUSION API - COMPREHENSIVE AUTHENTICATION TEST SUITE")
        print("="*80)
        print(f"Testing API key: {API_KEY}")
        print(f"Username: {USERNAME}")
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all test suites
        self.test_basic_variations()
        self.test_encoding_variations()
        self.test_header_variations()
        self.test_alternative_endpoints()
        self.test_no_auth_endpoints()
        self.test_advanced_scenarios()

        # Analyze results
        interesting, by_response, status_codes = self.analyze_results()

        print("\n" + "="*80)
        print("FINAL VERDICT")
        print("="*80)

        if interesting:
            print("\n✓ POTENTIALLY VALID: Some tests produced non-error responses!")
            print("  Review the 'INTERESTING RESPONSES' section above for details.")
        else:
            print("\n✗ API KEY APPEARS INVALID: All tests returned error messages.")
            print("  The API key 'C0H6-T2S9-H9A0-G0T9-X3N7' does not work with username 'scalmobile'.")
            print("\n  Possible reasons:")
            print("  1. This is a sample/dummy key from documentation")
            print("  2. The key is account-specific and tied to a different account")
            print("  3. The key has expired or been revoked")
            print("  4. The key requires additional activation or approval")
            print("  5. IP address whitelisting may be required")

        print(f"\n\nTest completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total tests run: {self.test_number}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
