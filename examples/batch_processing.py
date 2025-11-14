"""
Example 2: Batch Processing
============================
This example shows how to process multiple IMEIs from a CSV file.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_processor import BatchProcessor, progress_bar_callback


def main():
    """Batch process IMEIs from CSV"""

    # Create example CSV if it doesn't exist
    example_csv = Path("example_orders.csv")
    if not example_csv.exists():
        print("Creating example CSV file...")
        with open(example_csv, 'w') as f:
            f.write("imei,network_id,model_no\n")
            f.write("123456789012345,1,iPhone 12\n")
            f.write("123456789012346,1,iPhone 12 Pro\n")
            f.write("123456789012347,1,iPhone 13\n")
        print(f"Created: {example_csv}")

    print("\n" + "="*80)
    print("Batch Processing Example")
    print("="*80 + "\n")

    # Initialize processor with progress callback
    print("Initializing batch processor...")
    processor = BatchProcessor(progress_callback=progress_bar_callback)

    try:
        # Load orders from CSV
        print(f"\nLoading orders from: {example_csv}")
        orders = processor.load_from_csv(example_csv)
        print(f"Loaded {len(orders)} orders")

        # Process batch
        print("\nProcessing batch...")
        print("-" * 80)
        results = processor.process_batch(
            orders,
            delay_between_orders=0.5  # 0.5 seconds between orders
        )
        print("-" * 80)

        # Print summary
        processor.print_summary()

        # Show detailed results
        print("\nDetailed Results:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            status_icon = "✓" if result.success else "✗"
            print(f"\n{i}. {status_icon} IMEI: {result.imei}")
            print(f"   Network ID: {result.network_id}")
            if result.order_id:
                print(f"   Order ID: {result.order_id}")
            if result.status:
                print(f"   Status: {result.status}")
            if result.error:
                print(f"   Error: {result.error}")

        # Export results
        print("\n" + "="*80)
        print("Exporting results...")

        # Export to JSON
        json_file = Path("batch_results.json")
        processor.export_to_json(json_file)
        print(f"✓ Exported to JSON: {json_file}")

        # Export to CSV
        csv_file = Path("batch_results.csv")
        processor.export_to_csv(csv_file)
        print(f"✓ Exported to CSV: {csv_file}")

        # Optional: Check status of all orders
        print("\n" + "="*80)
        print("Checking status of all orders...")
        updated_results = processor.check_order_statuses()

        completed = sum(1 for r in updated_results if r.status == 'Completed')
        print(f"Completed orders: {completed}/{len(updated_results)}")

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "="*80)
    print("Done!")


if __name__ == "__main__":
    main()
