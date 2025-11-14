"""
GSM Fusion API Client Test Suite
=================================
Test suite for verifying API client functionality
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gsm_fusion_client import (
    GSMFusionClient,
    GSMFusionAPIError,
    OrderStatus,
    IMEIOrder,
    ServiceInfo
)


class TestGSMFusionClient:
    """Test suite for GSM Fusion Client"""

    def __init__(self):
        """Initialize test suite"""
        self.client = None
        self.test_results = []

    def setup(self):
        """Setup test environment"""
        print("Setting up test environment...")

        # Check for credentials
        if not os.getenv('GSM_FUSION_API_KEY'):
            print("⚠ Warning: GSM_FUSION_API_KEY not set")
            print("Set environment variables or create .env file to run tests")
            return False

        if not os.getenv('GSM_FUSION_USERNAME'):
            print("⚠ Warning: GSM_FUSION_USERNAME not set")
            return False

        try:
            self.client = GSMFusionClient()
            print("✓ Client initialized successfully")
            return True
        except GSMFusionAPIError as e:
            print(f"✗ Failed to initialize client: {e}")
            return False

    def teardown(self):
        """Cleanup after tests"""
        if self.client:
            self.client.close()
            print("\n✓ Client closed")

    def run_test(self, test_name: str, test_func):
        """Run a single test"""
        print(f"\nTest: {test_name}")
        print("-" * 80)

        try:
            test_func()
            print(f"✓ PASSED: {test_name}")
            self.test_results.append((test_name, True, None))
            return True
        except Exception as e:
            print(f"✗ FAILED: {test_name}")
            print(f"  Error: {str(e)}")
            self.test_results.append((test_name, False, str(e)))
            return False

    def test_get_imei_services(self):
        """Test: Get IMEI services list"""
        services = self.client.get_imei_services()

        assert isinstance(services, list), "Services should be a list"
        assert len(services) > 0, "Should have at least one service"

        # Check first service structure
        service = services[0]
        assert isinstance(service, ServiceInfo), "Should be ServiceInfo object"
        assert service.package_id, "Service should have package_id"
        assert service.title, "Service should have title"
        assert service.price, "Service should have price"

        print(f"  Retrieved {len(services)} IMEI services")
        print(f"  First service: {service.title} (${service.price})")

    def test_get_file_services(self):
        """Test: Get file services list"""
        services = self.client.get_file_services()

        assert isinstance(services, list), "Services should be a list"
        # May be empty, so just check type
        print(f"  Retrieved {len(services)} file services")

    def test_place_imei_order_invalid(self):
        """Test: Place IMEI order with invalid data (should fail gracefully)"""
        try:
            # Use obviously fake IMEI and service ID
            result = self.client.place_imei_order(
                imei="000000000000000",
                network_id="999999"
            )

            # If it doesn't raise an exception, check result
            if not result['orders'] and not result['duplicates']:
                print("  Order rejected as expected for invalid data")
            else:
                print("  ⚠ Warning: Invalid order was accepted")

        except GSMFusionAPIError:
            print("  Order rejected as expected (GSMFusionAPIError)")

    def test_get_imei_orders_nonexistent(self):
        """Test: Get non-existent order (should return empty or error)"""
        try:
            orders = self.client.get_imei_orders("999999999")

            if not orders:
                print("  Non-existent order returned empty list as expected")
            else:
                print(f"  Returned {len(orders)} orders")

        except GSMFusionAPIError:
            print("  Non-existent order raised error as expected")

    def test_context_manager(self):
        """Test: Context manager usage"""
        with GSMFusionClient() as client:
            services = client.get_imei_services()
            assert len(services) > 0, "Should retrieve services"

        print("  Context manager worked correctly")

    def test_error_handling(self):
        """Test: Error handling for missing credentials"""
        # Save current credentials
        api_key = os.getenv('GSM_FUSION_API_KEY')
        username = os.getenv('GSM_FUSION_USERNAME')

        # Test with missing API key
        os.environ.pop('GSM_FUSION_API_KEY', None)

        try:
            client = GSMFusionClient()
            assert False, "Should have raised error for missing API key"
        except GSMFusionAPIError as e:
            assert "API key is required" in str(e)
            print("  Correctly raised error for missing API key")

        # Restore credentials
        if api_key:
            os.environ['GSM_FUSION_API_KEY'] = api_key
        if username:
            os.environ['GSM_FUSION_USERNAME'] = username

    def test_multiple_imeis(self):
        """Test: Submit multiple IMEIs at once"""
        try:
            # Use fake IMEIs for testing
            imeis = ["000000000000001", "000000000000002"]

            result = self.client.place_imei_order(
                imei=imeis,
                network_id="1"
            )

            print(f"  Submitted {len(imeis)} IMEIs")
            print(f"  Results: {len(result['orders'])} orders, {len(result['duplicates'])} duplicates")

        except GSMFusionAPIError as e:
            print(f"  Multiple IMEI submission raised error: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("Test Summary")
        print("="*80)

        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = sum(1 for _, success, _ in self.test_results if not success)
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for name, success, error in self.test_results:
                if not success:
                    print(f"  - {name}: {error}")

        print("\n" + "="*80)

        return failed == 0

    def run_all_tests(self):
        """Run all tests"""
        print("="*80)
        print("GSM Fusion API Client Test Suite")
        print("="*80)

        if not self.setup():
            print("\n⚠ Setup failed. Cannot run tests.")
            print("Please set GSM_FUSION_API_KEY and GSM_FUSION_USERNAME environment variables")
            return False

        # Run tests
        tests = [
            ("Get IMEI Services", self.test_get_imei_services),
            ("Get File Services", self.test_get_file_services),
            ("Place Invalid IMEI Order", self.test_place_imei_order_invalid),
            ("Get Non-existent Order", self.test_get_imei_orders_nonexistent),
            ("Context Manager", self.test_context_manager),
            ("Error Handling", self.test_error_handling),
            ("Multiple IMEIs", self.test_multiple_imeis),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Print summary
        success = self.print_summary()

        # Cleanup
        self.teardown()

        return success


def main():
    """Main test runner"""
    test_suite = TestGSMFusionClient()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
