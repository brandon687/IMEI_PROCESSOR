"""
GSM Fusion Batch Processor
===========================
Automated batch processing system for handling multiple IMEI orders

Features:
- Process large batches of IMEIs from CSV/Excel files
- Automatic retry logic for failed orders
- Progress tracking and status updates
- Export results to various formats
- Scheduled batch processing
"""

import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError, IMEIOrder


logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result of a batch operation"""
    imei: str
    network_id: str
    order_id: Optional[str] = None
    status: Optional[str] = None
    code: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    timestamp: str = ""
    attempts: int = 1

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class BatchProcessor:
    """Batch processing system for GSM Fusion API"""

    def __init__(
        self,
        client: Optional[GSMFusionClient] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize batch processor

        Args:
            client: GSMFusionClient instance (creates new if None)
            max_retries: Maximum retry attempts for failed orders
            retry_delay: Delay between retries in seconds
            progress_callback: Optional callback function for progress updates
        """
        self.client = client or GSMFusionClient()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.progress_callback = progress_callback

        self.results: List[BatchResult] = []
        self.total_processed = 0
        self.total_success = 0
        self.total_failed = 0

    def load_from_csv(self, csv_file: Path) -> List[Dict]:
        """
        Load orders from CSV file

        CSV format:
            imei,network_id,model_no,operator_id,...
            123456789012345,1,,,...
            ...

        Args:
            csv_file: Path to CSV file

        Returns:
            List of order dictionaries
        """
        logger.info(f"Loading orders from CSV: {csv_file}")

        orders = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Remove empty values
                order = {k: v for k, v in row.items() if v}
                orders.append(order)

        logger.info(f"Loaded {len(orders)} orders from CSV")
        return orders

    def load_from_excel(self, excel_file: Path, sheet_name: str = 0) -> List[Dict]:
        """
        Load orders from Excel file

        Args:
            excel_file: Path to Excel file
            sheet_name: Sheet name or index (default: 0)

        Returns:
            List of order dictionaries
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for Excel support. Install with: pip install pandas openpyxl")

        logger.info(f"Loading orders from Excel: {excel_file}")

        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        # Remove rows with NaN values in required columns
        df = df.dropna(subset=['imei', 'network_id'])

        # Convert to list of dicts and remove NaN values
        orders = []
        for _, row in df.iterrows():
            order = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
            orders.append(order)

        logger.info(f"Loaded {len(orders)} orders from Excel")
        return orders

    def process_order(self, order: Dict, attempt: int = 1) -> BatchResult:
        """
        Process a single order

        Args:
            order: Order dictionary with 'imei' and 'network_id' required
            attempt: Current attempt number

        Returns:
            BatchResult object
        """
        imei = order['imei']
        network_id = order['network_id']

        # Extract optional parameters
        optional_params = {
            k: v for k, v in order.items()
            if k not in ['imei', 'network_id']
        }

        try:
            logger.debug(f"Processing IMEI: {imei} (attempt {attempt})")

            result = self.client.place_imei_order(
                imei=imei,
                network_id=network_id,
                **optional_params
            )

            if result['orders']:
                order_data = result['orders'][0]
                return BatchResult(
                    imei=imei,
                    network_id=network_id,
                    order_id=order_data['id'],
                    status=order_data['status'],
                    success=True,
                    attempts=attempt
                )

            elif result['duplicates']:
                return BatchResult(
                    imei=imei,
                    network_id=network_id,
                    success=False,
                    error='Duplicate IMEI',
                    attempts=attempt
                )

            else:
                return BatchResult(
                    imei=imei,
                    network_id=network_id,
                    success=False,
                    error='Unknown error',
                    attempts=attempt
                )

        except GSMFusionAPIError as e:
            logger.error(f"Error processing IMEI {imei}: {str(e)}")
            return BatchResult(
                imei=imei,
                network_id=network_id,
                success=False,
                error=str(e),
                attempts=attempt
            )

    def process_batch(
        self,
        orders: List[Dict],
        delay_between_orders: float = 0.5
    ) -> List[BatchResult]:
        """
        Process a batch of orders

        Args:
            orders: List of order dictionaries
            delay_between_orders: Delay between orders in seconds

        Returns:
            List of BatchResult objects
        """
        logger.info(f"Starting batch processing: {len(orders)} orders")

        self.results = []
        self.total_processed = 0
        self.total_success = 0
        self.total_failed = 0

        for i, order in enumerate(orders, 1):
            # Process order with retries
            result = self._process_with_retry(order)
            self.results.append(result)

            self.total_processed += 1
            if result.success:
                self.total_success += 1
            else:
                self.total_failed += 1

            # Call progress callback
            if self.progress_callback:
                self.progress_callback(
                    current=i,
                    total=len(orders),
                    result=result
                )

            # Delay between orders
            if i < len(orders):
                time.sleep(delay_between_orders)

        logger.info(
            f"Batch processing complete: "
            f"{self.total_success} success, {self.total_failed} failed"
        )

        return self.results

    def _process_with_retry(self, order: Dict) -> BatchResult:
        """Process order with retry logic"""
        last_result = None

        for attempt in range(1, self.max_retries + 1):
            result = self.process_order(order, attempt)

            if result.success:
                return result

            last_result = result

            # Don't retry for duplicates
            if result.error == 'Duplicate IMEI':
                break

            # Retry delay
            if attempt < self.max_retries:
                logger.debug(f"Retrying IMEI {order['imei']} in {self.retry_delay}s...")
                time.sleep(self.retry_delay)

        return last_result

    def check_order_statuses(
        self,
        results: Optional[List[BatchResult]] = None
    ) -> List[BatchResult]:
        """
        Check status of all orders in results

        Args:
            results: List of BatchResult objects (uses self.results if None)

        Returns:
            Updated list of BatchResult objects
        """
        if results is None:
            results = self.results

        logger.info(f"Checking status for {len(results)} orders")

        updated_results = []

        for result in results:
            if not result.order_id:
                updated_results.append(result)
                continue

            try:
                orders = self.client.get_imei_orders(result.order_id)
                if orders:
                    order = orders[0]
                    result.status = order.status
                    result.code = order.code

                updated_results.append(result)

            except GSMFusionAPIError as e:
                logger.error(f"Error checking order {result.order_id}: {str(e)}")
                updated_results.append(result)

        logger.info("Status check complete")
        return updated_results

    def wait_for_all_completions(
        self,
        results: Optional[List[BatchResult]] = None,
        check_interval: int = 60,
        timeout: int = 3600
    ) -> List[BatchResult]:
        """
        Wait for all orders to complete

        Args:
            results: List of BatchResult objects (uses self.results if None)
            check_interval: Seconds between status checks
            timeout: Maximum wait time in seconds

        Returns:
            Updated list of BatchResult objects
        """
        if results is None:
            results = self.results

        logger.info(f"Waiting for {len(results)} orders to complete")

        start_time = time.time()
        pending_results = [r for r in results if r.order_id]

        while pending_results:
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning("Timeout reached while waiting for orders")
                break

            # Check statuses
            results = self.check_order_statuses(results)

            # Update pending list
            pending_results = [
                r for r in results
                if r.order_id and r.status not in ['Completed', 'Rejected', None]
            ]

            if pending_results:
                logger.info(
                    f"{len(pending_results)} orders still pending. "
                    f"Checking again in {check_interval} seconds..."
                )
                time.sleep(check_interval)

        logger.info("All orders completed or timeout reached")
        return results

    def export_to_csv(self, output_file: Path, results: Optional[List[BatchResult]] = None):
        """Export results to CSV"""
        if results is None:
            results = self.results

        logger.info(f"Exporting results to CSV: {output_file}")

        with open(output_file, 'w', newline='') as f:
            if not results:
                return

            fieldnames = list(asdict(results[0]).keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for result in results:
                writer.writerow(asdict(result))

        logger.info(f"Exported {len(results)} results to CSV")

    def export_to_json(self, output_file: Path, results: Optional[List[BatchResult]] = None):
        """Export results to JSON"""
        if results is None:
            results = self.results

        logger.info(f"Exporting results to JSON: {output_file}")

        with open(output_file, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)

        logger.info(f"Exported {len(results)} results to JSON")

    def export_to_excel(self, output_file: Path, results: Optional[List[BatchResult]] = None):
        """Export results to Excel"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for Excel export. Install with: pip install pandas openpyxl")

        if results is None:
            results = self.results

        logger.info(f"Exporting results to Excel: {output_file}")

        df = pd.DataFrame([asdict(r) for r in results])
        df.to_excel(output_file, index=False)

        logger.info(f"Exported {len(results)} results to Excel")

    def get_summary(self, results: Optional[List[BatchResult]] = None) -> Dict:
        """Get summary statistics"""
        if results is None:
            results = self.results

        summary = {
            'total': len(results),
            'successful': sum(1 for r in results if r.success),
            'failed': sum(1 for r in results if not r.success),
            'duplicates': sum(1 for r in results if r.error == 'Duplicate IMEI'),
            'pending': sum(1 for r in results if r.status == 'Pending'),
            'completed': sum(1 for r in results if r.status == 'Completed'),
            'rejected': sum(1 for r in results if r.status == 'Rejected'),
            'in_process': sum(1 for r in results if r.status == 'In Process'),
        }

        return summary

    def print_summary(self, results: Optional[List[BatchResult]] = None):
        """Print summary to console"""
        summary = self.get_summary(results)

        print("\n" + "="*80)
        print("Batch Processing Summary")
        print("="*80)
        print(f"Total Orders:      {summary['total']}")
        print(f"Successful:        {summary['successful']}")
        print(f"Failed:            {summary['failed']}")
        print(f"Duplicates:        {summary['duplicates']}")
        print("\nOrder Status:")
        print(f"  Pending:         {summary['pending']}")
        print(f"  Completed:       {summary['completed']}")
        print(f"  Rejected:        {summary['rejected']}")
        print(f"  In Process:      {summary['in_process']}")
        print("="*80 + "\n")


def progress_bar_callback(current: int, total: int, result: BatchResult):
    """Simple progress bar callback"""
    percent = (current / total) * 100
    bar_length = 50
    filled = int(bar_length * current / total)
    bar = '█' * filled + '-' * (bar_length - filled)

    status = '✓' if result.success else '✗'
    print(f'\r[{bar}] {percent:.1f}% {status} {result.imei}', end='', flush=True)

    if current == total:
        print()  # New line at end


if __name__ == "__main__":
    # Example usage
    print("GSM Fusion Batch Processor")
    print("="*50)
    print("\nExample usage:")
    print("""
from batch_processor import BatchProcessor, progress_bar_callback

# Initialize processor
processor = BatchProcessor(progress_callback=progress_bar_callback)

# Load from CSV
orders = processor.load_from_csv('orders.csv')

# Process batch
results = processor.process_batch(orders)

# Print summary
processor.print_summary()

# Export results
processor.export_to_csv('results.csv')
processor.export_to_json('results.json')
    """)
