# Quick Start Guide - GSM Fusion API

## 🚀 Setup Complete!
Your API is configured and ready to use with:
- **API Key**: I7E1-K5C7-E8R5-P1V6-A2P8
- **Username**: scalmobile
- **Base URL**: https://hammerfusion.com

---

## 📋 Complete Order Flow

### 1️⃣ **Browse Available Services**
```bash
python3 gsm_cli.py services
```
Or search for specific services:
```bash
python3 gsm_cli.py services | grep "AT&T"
python3 gsm_cli.py services | grep "T-Mobile"
python3 gsm_cli.py services | grep "Checker"
```

**Output**: List of services with Service ID, Price, and Delivery Time

---

### 2️⃣ **Submit a Single IMEI Order**
```bash
python3 gsm_cli.py submit <IMEI> <SERVICE_ID>
```

**Example**:
```bash
python3 gsm_cli.py submit 359702373699048 1739
```

**Output**:
```
✓ Order Submitted Successfully:
Order ID: 54321
IMEI: 359702373699048
Status: Pending
```

💡 **Save the Order ID!** You'll need it to check status.

---

### 3️⃣ **Check Order Status**
```bash
python3 gsm_cli.py status <ORDER_ID>
```

**Example**:
```bash
python3 gsm_cli.py status 54321
```

**Output**:
```
Order ID: 54321
IMEI: 359702373699048
Package: Apple iPhone IMEI Checker
Status: Completed
Code: [Your results here]
```

---

### 4️⃣ **Extract Results**

When status = **Completed**, the `Code` field contains your data:

**For Checker Services** (like Service 1739):
- Carrier information
- Simlock status
- Find My iPhone status
- Warranty details
- Activation status
- Full device specifications

**For Unlock Services**:
- Unlock code or confirmation
- Instructions (if any)

**If Rejected**:
- Reason for rejection

---

## 🔄 Automated Workflow

### Option A: Wait for Completion Automatically
```bash
python3 gsm_cli.py wait <ORDER_ID>
```

This will:
- Check status every 60 seconds
- Notify you when completed
- Display final results automatically

**Example**:
```bash
python3 gsm_cli.py wait 54321
```

---

### Option B: Batch Processing (Multiple IMEIs)

**Step 1**: Create a CSV file `orders.csv`:
```csv
imei,network_id
359702373699048,1739
359702373699049,1739
359702373699050,1739
```

**Step 2**: Submit batch:
```bash
python3 gsm_cli.py batch orders.csv --output results.json
```

**Step 3**: Check results in `results.json`:
```json
[
  {
    "imei": "359702373699048",
    "order_id": "54321",
    "status": "Pending",
    "success": true,
    "error": null
  },
  {
    "imei": "359702373699049",
    "order_id": "54322",
    "status": "Pending",
    "success": true,
    "error": null
  }
]
```

---

## 💰 Popular Services

| Service ID | Service Name | Price | Delivery |
|------------|-------------|-------|----------|
| 1739 | iPhone IMEI Checker (Carrier/FMI/etc) | $0.08 | Instant-5 Min |
| 1693 | AT&T iPhone Unlock [Past Due] | $30.00 | 1-3 Days |
| 1239 | AT&T iPhone Unlock [60 Days] | $19.90 | 12-72 Hours |
| 1724 | T-Mobile iPhone Unlock (i15 Series) | $185.00 | 24-72 Hours |

---

## 📊 Data Extraction Methods

### Method 1: Command Line (Manual)
```bash
# Submit order
python3 gsm_cli.py submit 359702373699048 1739

# Check status repeatedly until completed
python3 gsm_cli.py status 54321
```

### Method 2: Python Script (Automated)
```python
from gsm_fusion_client import GSMFusionClient

client = GSMFusionClient()

# Submit order
result = client.place_imei_order(
    imei="359702373699048",
    network_id="1739"
)

order_id = result['orders'][0]['id']
print(f"Order ID: {order_id}")

# Wait for completion
completed_order = client.wait_for_order_completion(
    order_id=order_id,
    check_interval=60  # Check every 60 seconds
)

print(f"Result: {completed_order.code}")
client.close()
```

### Method 3: Batch with Results Export
```bash
# Process multiple IMEIs and save results
python3 gsm_cli.py batch orders.csv --output results.json

# Parse results programmatically
import json
with open('results.json') as f:
    orders = json.load(f)
    for order in orders:
        print(f"{order['imei']}: {order['status']}")
```

---

## 🛠️ Advanced Options

### Submit with Additional Parameters
Some services require extra parameters:

```bash
python3 gsm_cli.py submit 359702373699048 1239 \
  --model-no "iPhone 14 Pro" \
  --serial-no "G540J7W46Q"
```

Available parameters:
- `--model-no`: Device model
- `--operator-id`: Carrier/operator ID
- `--serial-no`: Serial number
- `--mep`: MEP value (BlackBerry)
- `--prd`: PRD code

---

## ⚠️ Important Notes

1. **Save Order IDs**: Always save the order ID returned when submitting
2. **Check Service Requirements**: Some services need specific parameters
3. **Delivery Times Vary**:
   - Instant services: 1-5 minutes
   - Standard: 12-72 hours
   - Complex unlocks: 1-7 days
4. **Balance Required**: Ensure sufficient balance for orders
5. **Valid IMEIs Only**: Use valid 15-digit IMEI numbers

---

## 📞 Quick Commands Reference

```bash
# List all services
python3 gsm_cli.py services

# List file services
python3 gsm_cli.py services --type file

# Submit single order
python3 gsm_cli.py submit <IMEI> <SERVICE_ID>

# Check status
python3 gsm_cli.py status <ORDER_ID>

# Check multiple orders
python3 gsm_cli.py status 12345,12346,12347

# Wait for completion
python3 gsm_cli.py wait <ORDER_ID>

# Batch process
python3 gsm_cli.py batch orders.csv --output results.json
```

---

## 🔍 Troubleshooting

**"Invalid API Key"**: Check .env file has correct key
**"Order not found"**: Wait a few seconds after submission
**"Request timeout"**: Check internet connection
**"Service rejected"**: Check IMEI validity and service requirements

---

## 📚 Documentation Files

- `README.md` - Full documentation
- `COMMANDS.md` - All available commands
- `order_flow_demo.py` - Interactive demo
- `examples/` - Code examples

---

**Ready to start!** 🎉

Try your first order:
```bash
python3 gsm_cli.py services | head -20
```
