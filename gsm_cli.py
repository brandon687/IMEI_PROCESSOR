#!/usr/bin/env python3
"""
GSM Fusion CLI Tool
===================
Command-line interface for GSM Fusion API operations

Usage:
    python gsm_cli.py services          # List available services
    python gsm_cli.py submit <imei> <service_id>    # Submit single IMEI
    python gsm_cli.py status <order_id>             # Check order status
    python gsm_cli.py batch <csv_file>              # Batch process from CSV
"""

import sys
import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Optional
from tabulate import tabulate
from dotenv import load_dotenv

from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError

# Load environment variables from .env file
load_dotenv()


class GSMFusionCLI:
    """CLI interface for GSM Fusion API"""

    def __init__(self):
        self.client = GSMFusionClient()

    def list_services(self, service_type: str = 'imei'):
        """List available services"""
        print(f"\n{'='*80}")
        print(f"GSM Fusion - Available {service_type.upper()} Services")
        print(f"{'='*80}\n")

        try:
            if service_type.lower() == 'imei':
                services = self.client.get_imei_services()
            else:
                services = self.client.get_file_services()

            if not services:
                print("No services found.")
                return

            # Prepare table data
            table_data = []
            for service in services:
                table_data.append([
                    service.package_id,
                    service.category,
                    service.title,
                    f"${service.price}",
                    service.delivery_time,
                    service.details[:50] + '...' if len(service.details) > 50 else service.details
                ])

            headers = ['Service ID', 'Category', 'Service Name', 'Price', 'Delivery Time', 'Details']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nTotal services: {len(services)}")

        except GSMFusionAPIError as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def submit_order(self, imei: str, network_id: str, **kwargs):
        """Submit a single IMEI order"""
        print(f"\n{'='*80}")
        print(f"Submitting IMEI Order")
        print(f"{'='*80}\n")

        try:
            print(f"IMEI: {imei}")
            print(f"Network/Service ID: {network_id}")

            if kwargs:
                print("\nAdditional Parameters:")
                for key, value in kwargs.items():
                    print(f"  {key}: {value}")

            print("\nSubmitting order...")

            result = self.client.place_imei_order(
                imei=imei,
                network_id=network_id,
                **kwargs
            )

            # Display results
            if result['orders']:
                print("\n✓ Order Submitted Successfully:")
                table_data = []
                for order in result['orders']:
                    table_data.append([
                        order['id'],
                        order['imei'],
                        order['status']
                    ])
                headers = ['Order ID', 'IMEI', 'Status']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))

            if result['duplicates']:
                print("\n⚠ Duplicate IMEIs (already in system):")
                for dup in result['duplicates']:
                    print(f"  - {dup}")

            if result['errors']:
                print("\n✗ Errors:")
                for error in result['errors']:
                    print(f"  - {error}")

        except GSMFusionAPIError as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def check_status(self, order_ids: List[str]):
        """Check status of orders"""
        print(f"\n{'='*80}")
        print(f"Order Status Check")
        print(f"{'='*80}\n")

        try:
            orders = self.client.get_imei_orders(order_ids)

            if not orders:
                print("No orders found.")
                return

            # Prepare table data
            table_data = []
            for order in orders:
                table_data.append([
                    order.id,
                    order.imei,
                    order.package,
                    order.status,
                    order.code or 'N/A',
                    order.requested_at or 'N/A'
                ])

            headers = ['Order ID', 'IMEI', 'Package', 'Status', 'Code', 'Requested At']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))

        except GSMFusionAPIError as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def batch_submit(self, csv_file: Path, output_file: Optional[Path] = None):
        """Batch submit orders from CSV file"""
        print(f"\n{'='*80}")
        print(f"Batch Order Submission")
        print(f"{'='*80}\n")

        if not csv_file.exists():
            print(f"Error: File not found: {csv_file}", file=sys.stderr)
            sys.exit(1)

        try:
            # Read CSV file
            print(f"Reading CSV file: {csv_file}")
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            print(f"Found {len(rows)} rows to process\n")

            # Validate required columns
            if not rows:
                print("Error: CSV file is empty", file=sys.stderr)
                sys.exit(1)

            required_cols = ['imei', 'network_id']
            if not all(col in rows[0] for col in required_cols):
                print(f"Error: CSV must contain columns: {', '.join(required_cols)}", file=sys.stderr)
                sys.exit(1)

            # Process each row
            results = []
            for i, row in enumerate(rows, 1):
                imei = row['imei']
                network_id = row['network_id']

                print(f"[{i}/{len(rows)}] Processing IMEI: {imei}")

                try:
                    # Extract optional parameters
                    optional_params = {
                        k: v for k, v in row.items()
                        if k not in required_cols and v
                    }

                    result = self.client.place_imei_order(
                        imei=imei,
                        network_id=network_id,
                        **optional_params
                    )

                    if result['orders']:
                        order = result['orders'][0]
                        print(f"  ✓ Order ID: {order['id']} - Status: {order['status']}")
                        results.append({
                            'imei': imei,
                            'order_id': order['id'],
                            'status': order['status'],
                            'success': True,
                            'error': None
                        })
                    elif result['duplicates']:
                        print(f"  ⚠ Duplicate IMEI")
                        results.append({
                            'imei': imei,
                            'order_id': None,
                            'status': 'duplicate',
                            'success': False,
                            'error': 'Duplicate IMEI'
                        })

                except GSMFusionAPIError as e:
                    print(f"  ✗ Error: {str(e)}")
                    results.append({
                        'imei': imei,
                        'order_id': None,
                        'status': 'error',
                        'success': False,
                        'error': str(e)
                    })

            # Summary
            print(f"\n{'='*80}")
            print("Batch Processing Summary")
            print(f"{'='*80}\n")

            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count

            print(f"Total Processed: {len(results)}")
            print(f"Successful: {success_count}")
            print(f"Failed: {fail_count}")

            # Save results
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nResults saved to: {output_file}")

        except Exception as e:
            print(f"\nError during batch processing: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def wait_for_completion(self, order_id: str, check_interval: int = 60):
        """Wait for order to complete"""
        print(f"\n{'='*80}")
        print(f"Waiting for Order Completion")
        print(f"{'='*80}\n")

        try:
            print(f"Order ID: {order_id}")
            print(f"Check interval: {check_interval} seconds")
            print("\nMonitoring order status...\n")

            order = self.client.wait_for_order_completion(
                order_id=order_id,
                check_interval=check_interval
            )

            print("\n✓ Order Completed!")
            print(f"\nIMEI: {order.imei}")
            print(f"Status: {order.status}")
            print(f"Code: {order.code or 'N/A'}")
            print(f"Package: {order.package}")

        except GSMFusionAPIError as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='GSM Fusion API Command Line Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available IMEI services
  %(prog)s services

  # List file services
  %(prog)s services --type file

  # Submit single IMEI order
  %(prog)s submit 123456789012345 1

  # Submit with optional parameters
  %(prog)s submit 123456789012345 1 --model-no "iPhone 12"

  # Check order status
  %(prog)s status 12345

  # Check multiple orders
  %(prog)s status 12345,12346,12347

  # Batch submit from CSV
  %(prog)s batch orders.csv

  # Batch submit and save results
  %(prog)s batch orders.csv --output results.json

  # Wait for order completion
  %(prog)s wait 12345

Environment Variables:
  GSM_FUSION_API_KEY     API key for authentication
  GSM_FUSION_USERNAME    Username for authentication
  GSM_FUSION_BASE_URL    Base URL (default: https://hammerfusion.com)
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Services command
    services_parser = subparsers.add_parser('services', help='List available services')
    services_parser.add_argument(
        '--type',
        choices=['imei', 'file'],
        default='imei',
        help='Service type (default: imei)'
    )

    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit IMEI order')
    submit_parser.add_argument('imei', help='IMEI number')
    submit_parser.add_argument('network_id', help='Network/Service ID')
    submit_parser.add_argument('--model-no', help='Model number')
    submit_parser.add_argument('--operator-id', help='Operator ID')
    submit_parser.add_argument('--service-id', help='Service ID')
    submit_parser.add_argument('--provider-id', help='Provider ID')
    submit_parser.add_argument('--model-id', help='Model ID')
    submit_parser.add_argument('--mobile-id', help='Mobile ID')
    submit_parser.add_argument('--mep', help='MEP value')
    submit_parser.add_argument('--serial-no', help='Serial number')
    submit_parser.add_argument('--prd', help='PRD code')
    submit_parser.add_argument('--pin', help='PIN')
    submit_parser.add_argument('--kbh', help='KBH')
    submit_parser.add_argument('--zte', help='ZTE model')
    submit_parser.add_argument('--other-id', help='Other ID')
    submit_parser.add_argument('--other', help='Other value')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check order status')
    status_parser.add_argument('order_ids', help='Order ID(s) - comma-separated for multiple')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch submit from CSV')
    batch_parser.add_argument('csv_file', type=Path, help='CSV file path')
    batch_parser.add_argument('--output', type=Path, help='Output file for results')

    # Wait command
    wait_parser = subparsers.add_parser('wait', help='Wait for order completion')
    wait_parser.add_argument('order_id', help='Order ID to monitor')
    wait_parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    cli = GSMFusionCLI()

    try:
        if args.command == 'services':
            cli.list_services(args.type)

        elif args.command == 'submit':
            # Build optional parameters
            optional_params = {}
            param_mapping = {
                'model_no': 'modelNo',
                'operator_id': 'operatorId',
                'service_id': 'serviceId',
                'provider_id': 'providerId',
                'model_id': 'modelId',
                'mobile_id': 'mobileId',
                'mep': 'mep',
                'serial_no': 'serialNo',
                'prd': 'prd',
                'pin': 'pin',
                'kbh': 'kbh',
                'zte': 'zte',
                'other_id': 'otherId',
                'other': 'other'
            }

            for arg_name, param_name in param_mapping.items():
                value = getattr(args, arg_name, None)
                if value:
                    optional_params[param_name] = value

            cli.submit_order(args.imei, args.network_id, **optional_params)

        elif args.command == 'status':
            order_ids = args.order_ids.split(',')
            cli.check_status(order_ids)

        elif args.command == 'batch':
            cli.batch_submit(args.csv_file, args.output)

        elif args.command == 'wait':
            cli.wait_for_completion(args.order_id, args.interval)

    finally:
        cli.client.close()


if __name__ == '__main__':
    main()
