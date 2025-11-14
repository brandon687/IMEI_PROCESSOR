# GSM Fusion API Client

Professional Python client for the GSM Fusion API (hammerfusion.com) that automates IMEI data processing and GSX detail retrieval.

## Features

- **Complete API Coverage** - All GSM Fusion API endpoints fully implemented
- **Batch Processing** - Process hundreds of IMEIs automatically from CSV/Excel
- **Robust Error Handling** - Automatic retries, comprehensive logging, and graceful error recovery
- **CLI Tool** - Simple command-line interface for quick operations
- **Progress Tracking** - Real-time progress updates during batch operations
- **Multiple Export Formats** - Export results to CSV, JSON, or Excel
- **Type Safety** - Full type hints for better code quality and IDE support
- **Production Ready** - Professional logging, configuration management, and error handling

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd HAMMER-API

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
GSM_FUSION_API_KEY=your-api-key-here
GSM_FUSION_USERNAME=your-username-here
GSM_FUSION_BASE_URL=http://hammerfusion.com
```

Or set environment variables:

```bash
export GSM_FUSION_API_KEY="XXXX-XXXX-XXXX-XXXX-XXXX"
export GSM_FUSION_USERNAME="your_username"
export GSM_FUSION_BASE_URL="http://hammerfusion.com"
```

### 3. Usage

#### Command Line Interface (CLI)

The CLI tool provides the fastest way to interact with the API:

```bash
# Make the CLI executable
chmod +x gsm_cli.py

# List available services
python gsm_cli.py services

# Submit single IMEI order
python gsm_cli.py submit 123456789012345 1

# Check order status
python gsm_cli.py status 12345

# Batch process from CSV file
python gsm_cli.py batch orders.csv --output results.json

# Wait for order completion (with polling)
python gsm_cli.py wait 12345 --interval 30
```

#### Python API

Use the Python API for programmatic access:

```python
from gsm_fusion_client import GSMFusionClient

# Initialize client
client = GSMFusionClient()

# List available services
services = client.get_imei_services()
for service in services:
    print(f"{service.title}: ${service.price} ({service.delivery_time})")

# Submit IMEI order
result = client.place_imei_order(
    imei="123456789012345",
    network_id="1"
)

if result['orders']:
    order_id = result['orders'][0]['id']
    print(f"Order submitted: {order_id}")

# Check order status
orders = client.get_imei_orders(order_id)
for order in orders:
    print(f"Status: {order.status}")
    if order.code:
        print(f"Code: {order.code}")

# Close client when done
client.close()
```

#### Batch Processing

For processing large volumes of IMEIs:

```python
from batch_processor import BatchProcessor, progress_bar_callback

# Initialize processor with progress tracking
processor = BatchProcessor(progress_callback=progress_bar_callback)

# Load orders from CSV
orders = processor.load_from_csv('orders.csv')

# Or load from Excel
# orders = processor.load_from_excel('orders.xlsx')

# Process batch
results = processor.process_batch(orders)

# Print summary
processor.print_summary()

# Export results
processor.export_to_csv('results.csv')
processor.export_to_json('results.json')

# Check status of all orders
updated_results = processor.check_order_statuses()

# Wait for all orders to complete
final_results = processor.wait_for_all_completions(
    check_interval=60,  # Check every 60 seconds
    timeout=3600        # Timeout after 1 hour
)
```

## CSV File Format

For batch processing, create a CSV file with the following format:

```csv
imei,network_id,model_no,operator_id
123456789012345,1,iPhone 12,
123456789012346,1,iPhone 12,
123456789012347,2,,5
```

**Required columns:**
- `imei` - IMEI number(s), comma-separated for multiple
- `network_id` - Network/Service ID

**Optional columns:**
- `model_no` - Model number
- `operator_id` - Operator ID
- `service_id` - Service ID
- `provider_id` - Provider ID
- `model_id` - Model ID
- `mobile_id` - Mobile ID
- `mep` - MEP value (for BlackBerry services)
- `serial_no` - Serial number
- `prd` - PRD code
- `pin` - PIN
- `kbh` - KBH
- `zte` - ZTE model
- `other_id` - Other ID
- `other` - Other value

## API Reference

### GSMFusionClient

#### Methods

##### `get_imei_services() -> List[ServiceInfo]`
Get list of all available IMEI services.

##### `get_file_services() -> List[ServiceInfo]`
Get list of all available file services.

##### `place_imei_order(imei: str, network_id: str, **kwargs) -> Dict`
Submit IMEI order(s). Supports single or multiple IMEIs.

##### `get_imei_orders(order_ids: str | List[str]) -> List[IMEIOrder]`
Get status of IMEI orders.

##### `place_file_order(network_id: str, file_name: str, file_data: bytes) -> Dict`
Submit file order (.bcl or other files).

##### `get_file_order(order_id: str) -> Dict`
Get status of file order.

##### `wait_for_order_completion(order_id: str, check_interval: int = 60, max_wait_time: int = 3600) -> IMEIOrder`
Wait for an order to complete (with polling).

### BatchProcessor

#### Methods

##### `load_from_csv(csv_file: Path) -> List[Dict]`
Load orders from CSV file.

##### `load_from_excel(excel_file: Path, sheet_name: str = 0) -> List[Dict]`
Load orders from Excel file.

##### `process_batch(orders: List[Dict], delay_between_orders: float = 0.5) -> List[BatchResult]`
Process a batch of orders with automatic retry logic.

##### `check_order_statuses(results: List[BatchResult] = None) -> List[BatchResult]`
Check status of all orders.

##### `wait_for_all_completions(results: List[BatchResult] = None, check_interval: int = 60, timeout: int = 3600) -> List[BatchResult]`
Wait for all orders to complete.

##### `export_to_csv(output_file: Path, results: List[BatchResult] = None)`
Export results to CSV file.

##### `export_to_json(output_file: Path, results: List[BatchResult] = None)`
Export results to JSON file.

##### `export_to_excel(output_file: Path, results: List[BatchResult] = None)`
Export results to Excel file.

##### `get_summary(results: List[BatchResult] = None) -> Dict`
Get summary statistics.

## Advanced Usage

### Custom Configuration

```python
from gsm_fusion_client import GSMFusionClient

# Custom configuration
client = GSMFusionClient(
    api_key="your-key",
    username="your-username",
    base_url="http://hammerfusion.com",
    timeout=60,      # Request timeout in seconds
    max_retries=5    # Maximum retry attempts
)
```

### Using Context Manager

```python
# Automatically closes session when done
with GSMFusionClient() as client:
    services = client.get_imei_services()
    # ... do work ...
```

### Custom Progress Tracking

```python
from batch_processor import BatchProcessor

def my_progress_callback(current, total, result):
    """Custom progress handler"""
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}% - IMEI: {result.imei}")

    # Log to database, send notification, etc.
    if result.success:
        save_to_database(result)
    else:
        send_alert(result.error)

processor = BatchProcessor(progress_callback=my_progress_callback)
```

### Retry Configuration

```python
from batch_processor import BatchProcessor

processor = BatchProcessor(
    max_retries=5,        # Try up to 5 times
    retry_delay=10        # Wait 10 seconds between retries
)
```

### Error Handling

```python
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError

client = GSMFusionClient()

try:
    result = client.place_imei_order(imei="123456789012345", network_id="1")
except GSMFusionAPIError as e:
    print(f"API Error: {e}")
    # Handle error appropriately
```

## Order Status Codes

- `1` - Pending
- `2` - Completed
- `3` - Rejected
- `4` - In Process

## Logging

The client uses Python's standard logging module. Configure logging level:

```python
import logging

# Set log level
logging.basicConfig(level=logging.DEBUG)

# Or use environment variable
# LOG_LEVEL=DEBUG python gsm_cli.py services
```

## Examples

### Example 1: Simple IMEI Submission

```python
from gsm_fusion_client import GSMFusionClient

with GSMFusionClient() as client:
    # Submit order
    result = client.place_imei_order(
        imei="123456789012345",
        network_id="1"
    )

    # Get order ID
    order_id = result['orders'][0]['id']

    # Wait for completion
    completed_order = client.wait_for_order_completion(order_id)

    print(f"Code: {completed_order.code}")
```

### Example 2: Batch Processing with Status Monitoring

```python
from batch_processor import BatchProcessor

processor = BatchProcessor()

# Load and process
orders = processor.load_from_csv('daily_orders.csv')
results = processor.process_batch(orders)

# Wait for all to complete
final_results = processor.wait_for_all_completions()

# Export
processor.export_to_excel('completed_orders.xlsx')
processor.print_summary()
```

### Example 3: Scheduled Batch Processing

```python
import schedule
import time
from batch_processor import BatchProcessor

def process_daily_orders():
    """Process orders from daily CSV file"""
    processor = BatchProcessor()
    orders = processor.load_from_csv('daily_orders.csv')
    results = processor.process_batch(orders)
    processor.export_to_json(f'results_{datetime.now():%Y%m%d}.json')
    processor.print_summary()

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(process_daily_orders)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Example 4: iPhone GSX Data Automation

```python
from gsm_fusion_client import GSMFusionClient

def check_iphone_gsx(imei: str) -> dict:
    """
    Check GSX details for an iPhone

    Args:
        imei: iPhone IMEI number

    Returns:
        Dictionary with GSX details
    """
    with GSMFusionClient() as client:
        # Get available services to find GSX service
        services = client.get_imei_services()
        gsx_service = next(
            (s for s in services if 'GSX' in s.title.upper()),
            None
        )

        if not gsx_service:
            raise ValueError("GSX service not found")

        # Submit order
        result = client.place_imei_order(
            imei=imei,
            network_id=gsx_service.package_id
        )

        if not result['orders']:
            raise ValueError("Failed to submit order")

        order_id = result['orders'][0]['id']

        # Wait for completion (GSX checks usually take 1-5 minutes)
        completed_order = client.wait_for_order_completion(
            order_id=order_id,
            check_interval=30,  # Check every 30 seconds
            max_wait_time=600   # Timeout after 10 minutes
        )

        return {
            'imei': imei,
            'status': completed_order.status,
            'data': completed_order.code,
            'package': completed_order.package
        }

# Usage
gsx_info = check_iphone_gsx("123456789012345")
print(f"GSX Data: {gsx_info['data']}")
```

## Troubleshooting

### API Key Not Found

```
Error: API key is required. Set GSM_FUSION_API_KEY environment variable...
```

**Solution:** Set the environment variable or create a `.env` file with your credentials.

### Connection Timeout

```
Error: Request timed out after 30 seconds
```

**Solution:** Increase timeout or check your internet connection.

```python
client = GSMFusionClient(timeout=60)
```

### Duplicate IMEI

If you receive duplicate IMEI errors, the IMEI has already been submitted. Check the status of existing orders.

### Import Errors

```
ImportError: pandas is required for Excel support
```

**Solution:** Install optional dependencies:

```bash
pip install pandas openpyxl
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables or `.env` files (add `.env` to `.gitignore`)
2. **Secure API keys** - Treat API keys like passwords
3. **Use HTTPS** - Ensure base URL uses HTTPS when available
4. **Rotate keys** - Regularly regenerate API keys
5. **Limit access** - Only share credentials with authorized personnel

## Performance Tips

1. **Batch processing** - Use batch processor for multiple IMEIs instead of individual submissions
2. **Adjust delays** - Reduce `delay_between_orders` for faster processing (but respect rate limits)
3. **Parallel processing** - For very large batches, consider splitting across multiple processes
4. **Caching** - Cache service lists to avoid repeated API calls

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the API documentation (GSM_Fusion_API.pdf)
3. Check logs for detailed error messages
4. Contact GSM Fusion support

## License

This client is provided as-is for use with the GSM Fusion API service.

## Changelog

### Version 1.0.0 (2025-11-12)
- Initial release
- Complete API coverage
- CLI tool
- Batch processing
- Excel/CSV support
- Comprehensive error handling
- Progress tracking
- Multiple export formats
