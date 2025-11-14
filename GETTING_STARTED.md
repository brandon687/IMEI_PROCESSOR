# Getting Started with GSM Fusion API Automation

## What You Have

You now have a **complete, production-ready automation system** that eliminates the need to manually log into hammerfusion.com. This system includes:

### 🎯 Core Components

1. **gsm_fusion_client.py** (600+ lines)
   - Professional Python API client
   - All GSM Fusion endpoints implemented
   - Automatic retry logic and error handling
   - Type-safe with full documentation

2. **gsm_cli.py** (400+ lines)
   - Command-line interface for quick operations
   - List services, submit orders, check status
   - Batch processing from CSV files
   - Beautiful formatted output

3. **batch_processor.py** (500+ lines)
   - Automated bulk processing system
   - CSV/Excel file support
   - Progress tracking and reporting
   - Multiple export formats

### 📚 Documentation

- **README.md** - Complete reference (400+ lines)
- **QUICKSTART.md** - Get started in 5 minutes
- **IMPLEMENTATION_GUIDE.md** - Integration scenarios
- **PROJECT_SUMMARY.md** - Overview and benefits
- **This file** - Getting started walkthrough

### 🧪 Examples & Testing

- **examples/** - Working code samples
  - simple_order.py - Basic IMEI submission
  - batch_processing.py - Bulk processing
  - iphone_automation.py - iPhone GSX automation
- **test_client.py** - Comprehensive test suite
- **verify_installation.py** - Installation checker

## Quick Start in 3 Steps

### Step 1: Install (2 minutes)

```bash
cd HAMMER-API

# Run automated setup
./setup.sh

# Or manually
pip install -r requirements.txt
```

### Step 2: Configure (1 minute)

Create `.env` file with your credentials:

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env  # or any text editor
```

Add your credentials:
```
GSM_FUSION_API_KEY=YOUR-API-KEY-HERE
GSM_FUSION_USERNAME=your_username
GSM_FUSION_BASE_URL=http://hammerfusion.com
```

### Step 3: Verify (1 minute)

```bash
# Test installation
python3 verify_installation.py

# Test API connection
python3 test_client.py
```

## Your First Automation (5 minutes)

### Option A: Command Line (Easiest)

```bash
# 1. List available services
python3 gsm_cli.py services

# 2. Submit an IMEI order (use actual values)
python3 gsm_cli.py submit 123456789012345 SERVICE_ID

# 3. Check order status
python3 gsm_cli.py status ORDER_ID
```

### Option B: Python Script (Most Flexible)

```python
from gsm_fusion_client import GSMFusionClient

# Initialize client
client = GSMFusionClient()

# Get available services
services = client.get_imei_services()
print(f"Available services: {len(services)}")

# Submit order
result = client.place_imei_order(
    imei="YOUR_IMEI",
    network_id="SERVICE_ID"
)

# Check result
if result['orders']:
    order_id = result['orders'][0]['id']
    print(f"Order submitted: {order_id}")

client.close()
```

### Option C: Batch Processing (Most Powerful)

```bash
# 1. Create CSV file (orders.csv)
cat > orders.csv << EOF
imei,network_id,model_no
123456789012345,1,iPhone 12
123456789012346,1,iPhone 13
EOF

# 2. Process batch
python3 gsm_cli.py batch orders.csv --output results.json

# Done! Results saved to results.json
```

## Common Workflows

### 1. Check Single iPhone IMEI

**Before (Manual - 2-3 minutes):**
1. Open browser
2. Log into hammerfusion.com
3. Navigate to form
4. Enter IMEI
5. Submit and wait
6. Check back later
7. Copy results

**After (Automated - 10 seconds):**
```bash
python3 gsm_cli.py submit IMEI SERVICE_ID
python3 gsm_cli.py status ORDER_ID
```

### 2. Process Daily Export

**Before (Manual - 2-4 hours):**
- Manually enter each IMEI
- Track progress in spreadsheet
- Check back multiple times
- Copy all results

**After (Automated - 5 minutes):**
```bash
# Export your data to CSV, then:
python3 gsm_cli.py batch daily_orders.csv
```

### 3. Monitor Order Until Complete

```bash
# Automatically polls until order completes
python3 gsm_cli.py wait ORDER_ID --interval 30
```

### 4. Integrate into Your App

```python
from gsm_fusion_client import GSMFusionClient

def check_imei_in_my_app(imei, service_id):
    """Integrate into your existing application"""
    client = GSMFusionClient()

    # Submit order
    result = client.place_imei_order(imei, service_id)
    order_id = result['orders'][0]['id']

    # Save to your database
    save_to_database(imei, order_id)

    # Wait for completion
    order = client.wait_for_order_completion(order_id)

    # Return result
    return {
        'status': order.status,
        'code': order.code,
        'package': order.package
    }
```

## Real-World Examples

All examples are in the `examples/` directory and can be run directly:

```bash
# Example 1: Simple order submission
python3 examples/simple_order.py

# Example 2: Batch processing
python3 examples/batch_processing.py

# Example 3: iPhone GSX automation
python3 examples/iphone_automation.py
```

## Time Savings Calculator

| Task | Manual Time | Automated Time | Savings |
|------|-------------|----------------|---------|
| Single IMEI | 2-3 min | 10 sec | 94% faster |
| 10 IMEIs | 20-30 min | 1 min | 97% faster |
| 100 IMEIs | 3-5 hours | 5 min | 98% faster |
| Daily batch (100) | 4 hours/day | 5 min/day | **~95 hours/month saved** |

## What Can You Automate?

### Immediate Wins
- ✅ No more manual login
- ✅ No more form filling
- ✅ No more waiting and checking back
- ✅ No more copy/paste of results
- ✅ No more manual spreadsheet updates

### Advanced Automation
- ✅ Scheduled daily/weekly processing
- ✅ Integration with your existing systems
- ✅ Real-time IMEI checking
- ✅ Automated reporting and alerts
- ✅ Batch processing of hundreds of IMEIs

## Integration Options

### 1. Standalone Tool
Use CLI for ad-hoc operations:
```bash
python3 gsm_cli.py submit IMEI SERVICE_ID
```

### 2. Scheduled Automation
Use cron for daily processing:
```bash
# Add to crontab: runs daily at 9 AM
0 9 * * * cd /path/to/HAMMER-API && python3 gsm_cli.py batch daily_orders.csv
```

### 3. Web Application
Integrate into Django/Flask:
```python
from gsm_fusion_client import GSMFusionClient

def my_view(request):
    client = GSMFusionClient()
    result = client.place_imei_order(imei, service_id)
    return JsonResponse(result)
```

### 4. API Microservice
Create REST API wrapper:
```python
from flask import Flask, request
from gsm_fusion_client import GSMFusionClient

app = Flask(__name__)

@app.route('/api/submit', methods=['POST'])
def submit():
    client = GSMFusionClient()
    return jsonify(client.place_imei_order(**request.json))
```

## Troubleshooting

### Installation Issues

**Problem:** Dependencies won't install
```bash
# Solution: Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** "API key is required"
```bash
# Solution: Check .env file exists and is configured
cat .env
# Should show your credentials
```

### Usage Issues

**Problem:** "Service not found"
```bash
# Solution: List available services first
python3 gsm_cli.py services
# Use the Service ID from the list
```

**Problem:** "Connection timeout"
```bash
# Solution: Check internet connection and try again
# Or increase timeout in code:
# client = GSMFusionClient(timeout=120)
```

## Next Steps

### Week 1: Get Familiar
1. ✅ Complete installation (done!)
2. ✅ Run examples in `examples/` directory
3. ✅ Test with a few real IMEIs
4. ✅ Review documentation

### Week 2: Integrate
1. ✅ Identify processes to automate
2. ✅ Create CSV exports from your system
3. ✅ Set up batch processing
4. ✅ Train your team on CLI

### Month 1: Optimize
1. ✅ Set up scheduled automation
2. ✅ Integrate into existing workflows
3. ✅ Add error monitoring
4. ✅ Measure time savings

## Support & Documentation

### Documentation Files
- **README.md** - Complete API reference
- **QUICKSTART.md** - 5-minute quick start
- **IMPLEMENTATION_GUIDE.md** - Integration patterns
- **PROJECT_SUMMARY.md** - Overview and benefits

### Getting Help
1. Check documentation in this directory
2. Review examples in `examples/` directory
3. Run `python3 test_client.py` to verify setup
4. Check logs for detailed error messages

### Common Commands Reference

```bash
# Installation
./setup.sh                              # Automated setup
python3 verify_installation.py          # Verify installation

# Testing
python3 test_client.py                  # Test API connection

# CLI Usage
python3 gsm_cli.py services             # List services
python3 gsm_cli.py submit IMEI ID       # Submit order
python3 gsm_cli.py status ORDER_ID      # Check status
python3 gsm_cli.py batch file.csv       # Batch process
python3 gsm_cli.py wait ORDER_ID        # Wait for completion

# Examples
python3 examples/simple_order.py        # Simple example
python3 examples/batch_processing.py    # Batch example
python3 examples/iphone_automation.py   # iPhone example
```

## Success Checklist

- [ ] Installed dependencies (`./setup.sh`)
- [ ] Configured credentials (`.env` file)
- [ ] Verified installation (`python3 verify_installation.py`)
- [ ] Tested connection (`python3 test_client.py`)
- [ ] Listed services (`python3 gsm_cli.py services`)
- [ ] Submitted test order
- [ ] Checked order status
- [ ] Tried batch processing
- [ ] Reviewed examples
- [ ] Read documentation

## You're Ready!

You now have everything you need to:
1. ✅ Eliminate manual website interactions
2. ✅ Automate IMEI processing
3. ✅ Batch process hundreds of orders
4. ✅ Integrate into your systems
5. ✅ Save hours of manual work daily

**Start with the Quick Start section above, and you'll be automating in minutes!**

---

**Questions?** Check the documentation files or run the examples to see it in action.

**Ready to automate?** Start with: `python3 gsm_cli.py services`
