# Quick Start Guide

Get started with the GSM Fusion API Client in 5 minutes.

## 1. Setup (2 minutes)

### Install Dependencies

```bash
cd HAMMER-API
pip install -r requirements.txt
```

### Configure Credentials

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
GSM_FUSION_API_KEY=XXXX-XXXX-XXXX-XXXX-XXXX
GSM_FUSION_USERNAME=your_username
GSM_FUSION_BASE_URL=http://hammerfusion.com
```

## 2. Test Connection (1 minute)

```bash
python test_client.py
```

If successful, you'll see:
```
✓ Client initialized successfully
✓ Retrieved X IMEI services
```

## 3. First Order (2 minutes)

### Using CLI

```bash
# List available services
python gsm_cli.py services

# Submit an order (replace with actual IMEI and service ID)
python gsm_cli.py submit YOUR_IMEI SERVICE_ID

# Check order status
python gsm_cli.py status ORDER_ID
```

### Using Python

```python
from gsm_fusion_client import GSMFusionClient

# Initialize
client = GSMFusionClient()

# List services
services = client.get_imei_services()
print(f"Available services: {len(services)}")

# Submit order
result = client.place_imei_order(
    imei="YOUR_IMEI",
    network_id="SERVICE_ID"
)

if result['orders']:
    print(f"Order ID: {result['orders'][0]['id']}")

client.close()
```

## 4. Batch Processing

### Prepare CSV File

Create `orders.csv`:
```csv
imei,network_id,model_no
123456789012345,1,iPhone 12
123456789012346,1,iPhone 13
```

### Run Batch

```bash
python gsm_cli.py batch orders.csv --output results.json
```

Or use Python:

```python
from batch_processor import BatchProcessor

processor = BatchProcessor()
orders = processor.load_from_csv('orders.csv')
results = processor.process_batch(orders)
processor.print_summary()
```

## Common Use Cases

### Check iPhone GSX Data

```bash
# Submit GSX check
python gsm_cli.py submit IMEI_NUMBER GSX_SERVICE_ID

# Wait for completion
python gsm_cli.py wait ORDER_ID
```

### Batch Process Daily Orders

```python
from batch_processor import BatchProcessor

processor = BatchProcessor()
orders = processor.load_from_csv('daily_orders.csv')
results = processor.process_batch(orders)
processor.export_to_excel('completed_orders.xlsx')
```

### Monitor Order Status

```python
from gsm_fusion_client import GSMFusionClient

client = GSMFusionClient()

# Wait for order to complete
order = client.wait_for_order_completion(
    order_id="12345",
    check_interval=30  # Check every 30 seconds
)

print(f"Status: {order.status}")
print(f"Code: {order.code}")
```

## Next Steps

- Read the full [README.md](README.md) for comprehensive documentation
- Check [examples/](examples/) directory for more examples
- Review [API Reference](README.md#api-reference) for all available methods

## Troubleshooting

### "API key is required"
- Make sure `.env` file exists and contains your API key
- Or set environment variable: `export GSM_FUSION_API_KEY="your-key"`

### "Connection timeout"
- Check your internet connection
- Verify the base URL is correct
- Try increasing timeout: `GSMFusionClient(timeout=60)`

### "Service not found"
- Run `python gsm_cli.py services` to see available service IDs
- Use the correct service ID from the list

## Support

- Check the [README.md](README.md) for detailed documentation
- Review [examples/](examples/) for code samples
- Contact GSM Fusion support for API-related issues
