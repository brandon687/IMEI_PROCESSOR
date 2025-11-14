"""
Example 3: iPhone GSX Data Automation
======================================
This example shows how to automate pulling GSX details for iPhones.
"""

import sys
import os
from typing import Dict, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError


class iPhoneGSXChecker:
    """Automated iPhone GSX data checker"""

    def __init__(self):
        self.client = GSMFusionClient()
        self.gsx_service_id = None

    def find_gsx_service(self) -> Optional[str]:
        """Find GSX service ID from available services"""
        print("Finding GSX service...")

        services = self.client.get_imei_services()

        # Look for GSX-related service
        for service in services:
            if any(keyword in service.title.upper() for keyword in ['GSX', 'APPLE', 'IPHONE']):
                print(f"Found service: {service.title} (ID: {service.package_id})")
                return service.package_id

        return None

    def check_gsx(self, imei: str, wait_for_result: bool = True) -> Dict:
        """
        Check GSX details for an iPhone

        Args:
            imei: iPhone IMEI number
            wait_for_result: If True, wait for order completion

        Returns:
            Dictionary with order information
        """
        print(f"\nChecking GSX for IMEI: {imei}")

        # Find GSX service if not already found
        if not self.gsx_service_id:
            self.gsx_service_id = self.find_gsx_service()
            if not self.gsx_service_id:
                raise ValueError(
                    "GSX service not found. Please check available services "
                    "and update the service ID manually."
                )

        # Submit order
        print("Submitting GSX check order...")
        result = self.client.place_imei_order(
            imei=imei,
            network_id=self.gsx_service_id
        )

        if not result['orders']:
            if result['duplicates']:
                return {
                    'imei': imei,
                    'status': 'duplicate',
                    'error': 'IMEI already in system'
                }
            else:
                return {
                    'imei': imei,
                    'status': 'failed',
                    'error': 'Failed to submit order'
                }

        order = result['orders'][0]
        order_id = order['id']

        print(f"✓ Order submitted: {order_id}")

        # Wait for completion if requested
        if wait_for_result:
            print("Waiting for GSX data (this may take 1-5 minutes)...")

            try:
                completed_order = self.client.wait_for_order_completion(
                    order_id=order_id,
                    check_interval=30,    # Check every 30 seconds
                    max_wait_time=600     # Timeout after 10 minutes
                )

                return {
                    'imei': imei,
                    'order_id': order_id,
                    'status': completed_order.status,
                    'gsx_data': completed_order.code,
                    'package': completed_order.package,
                    'requested_at': completed_order.requested_at
                }

            except GSMFusionAPIError as e:
                return {
                    'imei': imei,
                    'order_id': order_id,
                    'status': 'error',
                    'error': str(e)
                }
        else:
            # Return order ID for later checking
            return {
                'imei': imei,
                'order_id': order_id,
                'status': 'pending',
                'message': 'Order submitted, check status later'
            }

    def check_multiple_imeis(self, imeis: list, wait_for_results: bool = True) -> list:
        """
        Check GSX for multiple iPhones

        Args:
            imeis: List of IMEI numbers
            wait_for_results: If True, wait for all orders to complete

        Returns:
            List of result dictionaries
        """
        print(f"\nChecking GSX for {len(imeis)} iPhones...")
        print("="*80)

        results = []

        for i, imei in enumerate(imeis, 1):
            print(f"\n[{i}/{len(imeis)}]")
            result = self.check_gsx(imei, wait_for_result=wait_for_results)
            results.append(result)

        return results

    def close(self):
        """Close client connection"""
        self.client.close()


def main():
    """Main example"""
    print("="*80)
    print("iPhone GSX Data Automation")
    print("="*80)

    checker = iPhoneGSXChecker()

    try:
        # Example 1: Single IMEI check with wait
        print("\nExample 1: Single IMEI Check")
        print("-"*80)

        result = checker.check_gsx(
            imei="123456789012345",
            wait_for_result=False  # Set to True to wait for completion
        )

        print("\nResult:")
        for key, value in result.items():
            print(f"  {key}: {value}")

        # Example 2: Multiple IMEIs
        print("\n\n" + "="*80)
        print("Example 2: Multiple IMEI Checks")
        print("-"*80)

        imeis = [
            "123456789012345",
            "123456789012346",
            "123456789012347"
        ]

        results = checker.check_multiple_imeis(
            imeis,
            wait_for_results=False  # Set to True to wait for all completions
        )

        print("\n\nSummary:")
        print("-"*80)
        for i, result in enumerate(results, 1):
            status = result.get('status', 'unknown')
            order_id = result.get('order_id', 'N/A')
            print(f"{i}. IMEI: {result['imei']} - Status: {status} - Order: {order_id}")

        # Example 3: Check status of previous orders
        if any(r.get('order_id') for r in results):
            print("\n\n" + "="*80)
            print("Example 3: Check Status of Orders")
            print("-"*80)

            order_ids = [r['order_id'] for r in results if r.get('order_id')]
            if order_ids:
                print(f"\nChecking status for {len(order_ids)} orders...")
                orders = checker.client.get_imei_orders(order_ids)

                for order in orders:
                    print(f"\nOrder ID: {order.id}")
                    print(f"  IMEI: {order.imei}")
                    print(f"  Status: {order.status}")
                    if order.code:
                        print(f"  GSX Data: {order.code}")

    except GSMFusionAPIError as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

    finally:
        checker.close()

    print("\n" + "="*80)
    print("Done!")


if __name__ == "__main__":
    main()
