# Implementation Guide

This guide explains how to integrate the GSM Fusion API Client into your existing system to automate IMEI data processing.

## Overview

The GSM Fusion API Client provides three levels of automation:

1. **CLI Tool** - For manual/ad-hoc operations
2. **Python API** - For programmatic integration
3. **Batch Processor** - For automated bulk processing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  CLI Tool  │  │ Python API │  │  Batch Processor   │    │
│  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘    │
│        │               │                    │                │
│        └───────────────┴────────────────────┘                │
│                        │                                      │
│               ┌────────▼─────────┐                           │
│               │ GSMFusionClient  │                           │
│               └────────┬─────────┘                           │
│                        │                                      │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         │ HTTP/XML
                         ▼
                ┌────────────────┐
                │  GSM Fusion    │
                │  API Server    │
                │ (hammerfusion) │
                └────────────────┘
```

## Integration Scenarios

### Scenario 1: Manual Operations

**Use Case:** Staff manually checks individual IMEIs

**Solution:** Use CLI tool

```bash
# Staff runs this command
python gsm_cli.py submit IMEI SERVICE_ID
```

**Integration Steps:**
1. Install the tool on staff workstations
2. Configure credentials in `.env`
3. Train staff on CLI commands
4. Create shortcuts/aliases for common operations

### Scenario 2: Web Application Integration

**Use Case:** Your web app needs to check IMEI data

**Solution:** Use Python API directly

```python
# In your Django/Flask view
from gsm_fusion_client import GSMFusionClient

def check_imei_view(request):
    imei = request.POST.get('imei')
    service_id = request.POST.get('service_id')

    with GSMFusionClient() as client:
        result = client.place_imei_order(imei=imei, network_id=service_id)

        if result['orders']:
            order_id = result['orders'][0]['id']
            # Save order_id to your database
            save_order(imei, order_id)

    return JsonResponse({'order_id': order_id})
```

**Integration Steps:**
1. Add `gsm_fusion_client.py` to your project
2. Install dependencies: `pip install requests`
3. Configure credentials via environment variables
4. Create wrapper functions for your use cases
5. Add database models to track orders

### Scenario 3: Automated Daily Batch Processing

**Use Case:** Process hundreds of IMEIs daily from CSV exports

**Solution:** Use Batch Processor with scheduler

```python
# daily_processor.py
from batch_processor import BatchProcessor
from pathlib import Path
from datetime import datetime

def process_daily_orders():
    """Process daily CSV export"""
    processor = BatchProcessor()

    # Load from your daily export
    csv_file = Path('/path/to/daily_export.csv')
    orders = processor.load_from_csv(csv_file)

    # Process
    results = processor.process_batch(orders)

    # Export results
    output_file = Path(f'results_{datetime.now():%Y%m%d}.json')
    processor.export_to_json(output_file)

    # Import results back to your database
    import_results_to_database(results)

    return results

if __name__ == '__main__':
    process_daily_orders()
```

**Schedule with cron:**
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/HAMMER-API && python daily_processor.py
```

**Integration Steps:**
1. Set up automated CSV export from your system
2. Create processing script using `BatchProcessor`
3. Schedule with cron/Windows Task Scheduler
4. Set up error notifications (email, Slack, etc.)
5. Create dashboard to monitor results

### Scenario 4: Real-time API Integration

**Use Case:** Check IMEI in real-time when customer submits request

**Solution:** Async processing with callbacks

```python
# async_processor.py
import threading
from gsm_fusion_client import GSMFusionClient

class AsyncIMEIProcessor:
    def __init__(self):
        self.client = GSMFusionClient()

    def submit_order_async(self, imei, service_id, callback):
        """Submit order and call callback when done"""
        def process():
            try:
                # Submit order
                result = self.client.place_imei_order(imei, service_id)
                order_id = result['orders'][0]['id']

                # Wait for completion
                order = self.client.wait_for_order_completion(order_id)

                # Call callback with result
                callback(success=True, order=order)

            except Exception as e:
                callback(success=False, error=str(e))

        # Run in background thread
        thread = threading.Thread(target=process)
        thread.start()

# Usage
processor = AsyncIMEIProcessor()

def on_complete(success, order=None, error=None):
    if success:
        print(f"Order complete: {order.code}")
        update_customer_record(order)
    else:
        print(f"Order failed: {error}")
        notify_staff(error)

processor.submit_order_async("123456789012345", "1", on_complete)
```

### Scenario 5: Microservice Architecture

**Use Case:** GSM Fusion as a microservice

**Solution:** Create REST API wrapper

```python
# microservice.py
from flask import Flask, request, jsonify
from gsm_fusion_client import GSMFusionClient

app = Flask(__name__)
client = GSMFusionClient()

@app.route('/api/services', methods=['GET'])
def get_services():
    services = client.get_imei_services()
    return jsonify([{
        'id': s.package_id,
        'name': s.title,
        'price': s.price,
        'delivery_time': s.delivery_time
    } for s in services])

@app.route('/api/orders', methods=['POST'])
def submit_order():
    data = request.json
    result = client.place_imei_order(
        imei=data['imei'],
        network_id=data['service_id']
    )
    return jsonify(result)

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    orders = client.get_imei_orders(order_id)
    if orders:
        order = orders[0]
        return jsonify({
            'id': order.id,
            'imei': order.imei,
            'status': order.status,
            'code': order.code
        })
    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(port=5000)
```

## Best Practices

### 1. Error Handling

Always wrap API calls in try-except blocks:

```python
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError

try:
    client = GSMFusionClient()
    result = client.place_imei_order(imei, service_id)
except GSMFusionAPIError as e:
    # Handle API-specific errors
    log_error(f"API Error: {e}")
    notify_admin(e)
except Exception as e:
    # Handle unexpected errors
    log_error(f"Unexpected error: {e}")
```

### 2. Database Integration

Store order information in your database:

```python
# models.py (Django example)
from django.db import models

class IMEIOrder(models.Model):
    imei = models.CharField(max_length=15)
    service_id = models.CharField(max_length=50)
    order_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20)
    code = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gsm_fusion_orders'
```

### 3. Retry Logic

Use built-in retry mechanisms:

```python
from batch_processor import BatchProcessor

processor = BatchProcessor(
    max_retries=5,
    retry_delay=10
)
```

### 4. Logging

Configure comprehensive logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gsm_fusion.log'),
        logging.StreamHandler()
    ]
)
```

### 5. Monitoring

Track key metrics:

```python
class OrderMonitor:
    def __init__(self):
        self.total_orders = 0
        self.successful_orders = 0
        self.failed_orders = 0

    def track_order(self, result):
        self.total_orders += 1
        if result.success:
            self.successful_orders += 1
        else:
            self.failed_orders += 1

        # Alert if failure rate > 10%
        failure_rate = self.failed_orders / self.total_orders
        if failure_rate > 0.1:
            send_alert(f"High failure rate: {failure_rate:.1%}")
```

### 6. Credential Management

Use environment variables, not hardcoded credentials:

```python
# Good
client = GSMFusionClient()  # Reads from env vars

# Bad
client = GSMFusionClient(api_key="hardcoded-key")  # Never do this
```

### 7. Rate Limiting

Respect API rate limits:

```python
import time

def process_with_rate_limit(orders, requests_per_minute=60):
    delay = 60.0 / requests_per_minute

    for order in orders:
        process_order(order)
        time.sleep(delay)
```

## Testing Strategy

### Unit Tests

```python
# test_integration.py
import unittest
from gsm_fusion_client import GSMFusionClient

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.client = GSMFusionClient()

    def test_get_services(self):
        services = self.client.get_services()
        self.assertIsNotNone(services)
        self.assertGreater(len(services), 0)

    def tearDown(self):
        self.client.close()
```

### Integration Tests

```python
# test_end_to_end.py
def test_complete_workflow():
    # Submit order
    client = GSMFusionClient()
    result = client.place_imei_order("test_imei", "1")
    assert result['orders']

    order_id = result['orders'][0]['id']

    # Check status
    orders = client.get_imei_orders(order_id)
    assert len(orders) > 0
```

## Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure credentials (`.env` or environment variables)
- [ ] Test connection (`python test_client.py`)
- [ ] Set up logging
- [ ] Configure error notifications
- [ ] Set up monitoring/alerting
- [ ] Create backup/rollback plan
- [ ] Document internal procedures
- [ ] Train staff
- [ ] Set up scheduled tasks (if using batch processing)

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **HTTPS**: Use HTTPS for API URL when available
3. **Access Control**: Limit who can access credentials
4. **Logging**: Don't log sensitive data (API keys, full IMEI numbers)
5. **Updates**: Keep dependencies updated for security patches

## Performance Optimization

1. **Connection Pooling**: Reuse client instances
2. **Batch Processing**: Process multiple orders together
3. **Caching**: Cache service lists (update daily)
4. **Async Processing**: Use async for non-blocking operations
5. **Database Indexing**: Index order_id, imei columns

## Troubleshooting

### Common Issues

**Issue:** Orders timing out
- Increase timeout: `GSMFusionClient(timeout=120)`
- Check network connectivity

**Issue:** High failure rate
- Verify service IDs are correct
- Check account balance/status
- Review error messages in logs

**Issue:** Duplicate orders
- Check for existing orders before submitting
- Implement deduplication in your system

## Support and Maintenance

### Regular Maintenance

- Monitor error rates daily
- Review logs weekly
- Test API connectivity monthly
- Update dependencies quarterly
- Rotate API keys annually

### Getting Help

1. Check logs for error messages
2. Review API documentation (GSM_Fusion_API.pdf)
3. Test with `test_client.py`
4. Contact GSM Fusion support

## Next Steps

1. Choose integration scenario that fits your needs
2. Follow implementation steps
3. Test thoroughly
4. Deploy to production
5. Monitor and optimize

For questions or issues, refer to:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [examples/](examples/) - Code examples
