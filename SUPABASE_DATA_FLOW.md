# Supabase Data Flow - Complete Guide

**Status:** ✅ Supabase is SET UP and CONNECTED

---

## Overview

Your HAMMER-API system automatically collects and updates IMEI order data in Supabase (cloud PostgreSQL database). The system is **dual-mode**:

- **Development:** Uses SQLite (local file `imei_orders.db`)
- **Production:** Uses Supabase (cloud PostgreSQL)

**Auto-detection:** If `SUPABASE_URL` is set in `.env`, it uses Supabase. Otherwise, SQLite.

---

## Current Setup

✅ **Supabase Database:** https://opinemzfwtoduewqhqwp.supabase.co
✅ **Tables Created:** `orders`, `import_history`
✅ **Python Client:** Installed and working
✅ **Current Orders:** 0 (empty, ready to use)

---

## How Data Flows into Supabase

### Flow Diagram

```
┌─────────────────┐
│  User Submits   │
│  IMEI Order     │
│  (Web or CLI)   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  GSMFusionClient.place_imei_order() │
│  - Calls GSM Fusion API             │
│  - Gets order_id back               │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  database_supabase.insert_order()   │
│  - Stores in Supabase               │
│  - Status: "Pending"                │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Order stored in Supabase           │
│  (visible in web interface)         │
└─────────────────────────────────────┘
         │
         ↓ (Later...)
┌─────────────────────────────────────┐
│  Auto-Sync OR Manual Sync           │
│  - Checks order status with API     │
│  - Gets results (carrier, model)    │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  database_supabase.update_order()   │
│  - Updates status to "Completed"    │
│  - Adds carrier, model, simlock     │
│  - Adds result_code                 │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Order complete in Supabase         │
│  (all fields populated)             │
└─────────────────────────────────────┘
```

---

## Data Collection Points

### 1. Single Order Submission (Web Interface)

**File:** `web_app.py` → `/submit` route

```python
# User submits IMEI via web form
@app.route('/submit', methods=['POST'])
def submit_order():
    imei = request.form['imei']
    service_id = request.form['service_id']

    # Call GSM Fusion API
    with GSMFusionClient() as client:
        response = client.place_imei_order(imei, service_id)

    # Store in Supabase (auto-detected)
    db = get_database()  # Uses Supabase if configured
    db.insert_order({
        'order_id': response['order_id'],
        'imei': imei,
        'service_id': service_id,
        'status': 'Pending',
        'credits': response.get('charge'),
        'order_date': datetime.now()
    })

    # Order now in Supabase!
```

**Flow:**
1. User fills web form
2. API call to GSM Fusion
3. Response stored in Supabase
4. Status: "Pending"

---

### 2. Batch Upload (CSV)

**File:** `web_app.py` → `/batch` route

```python
# User uploads CSV file with IMEIs
@app.route('/batch', methods=['POST'])
def batch_upload():
    csv_file = request.files['file']

    # Parse CSV
    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():
        # Submit each IMEI
        with GSMFusionClient() as client:
            response = client.place_imei_order(
                row['imei'],
                row['service_id']
            )

        # Store in Supabase
        db = get_database()
        db.insert_order({
            'order_id': response['order_id'],
            'imei': row['imei'],
            'service_id': row['service_id'],
            'status': 'Pending',
            # ... other fields
        })

    # All orders now in Supabase!
```

**Flow:**
1. User uploads CSV with 100 IMEIs
2. System submits each to GSM Fusion API
3. Each response stored in Supabase
4. All 100 orders visible in database

---

### 3. Production Batch System

**File:** `production_submission_system.py`

```python
# Large-scale batch processing (6,000-20,000 IMEIs)
processor = ProductionSubmissionSystem()

result = processor.submit_batch([
    {'imei': '123...', 'service_id': 1},
    {'imei': '456...', 'service_id': 1},
    # ... 6,000 more
])

# Stores all orders in Supabase
# Uses atomic transactions
# Automatic rollback on failure
```

**Flow:**
1. Read large CSV file
2. Process in batches of 100
3. Submit to GSM Fusion API
4. Store all in Supabase
5. Checkpoint for crash recovery

---

### 4. Auto-Sync (Updates Pending Orders)

**File:** `web_app.py` → Background thread

```python
# Runs every 5 minutes automatically
def auto_sync_orders():
    db = get_database()  # Uses Supabase

    # Get all pending orders
    pending = db.get_orders_by_status('Pending')

    if pending:
        # Batch check status with API
        order_ids = [o['order_id'] for o in pending]

        with GSMFusionClient() as client:
            results = client.get_imei_orders(','.join(order_ids))

        # Update each order in Supabase
        for order in results['data']:
            if order['status_code'] == '2':  # Completed
                db.update_order_status(
                    order_id=order['id'],
                    status='Completed',
                    result_code=order.get('CODE'),
                    result_data={
                        'carrier': order.get('carrier'),
                        'model': order.get('model'),
                        'simlock': order.get('simlock'),
                        'fmi': order.get('fmi')
                    }
                )

        # Orders updated in Supabase!
```

**Flow:**
1. Timer triggers every 5 minutes
2. Finds all "Pending" orders
3. Checks status with GSM Fusion API
4. Updates Supabase with results
5. Status changes to "Completed"

---

### 5. Manual Sync (CLI)

**File:** `manual_sync.py`

```bash
python3 manual_sync.py
```

Does the same as auto-sync, but manually triggered.

---

## Database Operations

### Insert Order (Create)

```python
from database_supabase import get_database

db = get_database()  # Auto-uses Supabase if configured

db.insert_order({
    'order_id': '12345678',
    'imei': '356825821305851',
    'service_id': '1',
    'service_name': 'iPhone IMEI Info',
    'status': 'Pending',
    'credits': 0.50,
    'order_date': datetime.now()
})

# ✅ Order inserted into Supabase
```

---

### Update Order (Add Results)

```python
db.update_order_status(
    order_id='12345678',
    status='Completed',
    result_code='SUCCESS',
    result_code_display='SUCCESS',
    result_data={
        'carrier': 'Unlocked',
        'model': 'iPhone 13 128GB',
        'simlock': 'Unlocked',
        'fmi': 'OFF'
    }
)

# ✅ Order updated in Supabase
```

---

### Query Orders (Read)

```python
# Get recent orders
recent = db.get_recent_orders(limit=100)
# Returns: List of 100 most recent orders

# Get by IMEI
orders = db.get_orders_by_imei('356825821305851')
# Returns: All orders for this IMEI

# Get by status
pending = db.get_orders_by_status('Pending')
# Returns: All pending orders

# Get count
total = db.get_order_count()
# Returns: Total number of orders
```

---

## Data Schema in Supabase

### `orders` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-increment primary key |
| `order_id` | TEXT | GSM Fusion order ID (unique) |
| `service_name` | TEXT | Service name (e.g., "iPhone IMEI Info") |
| `service_id` | TEXT | Service package ID |
| `imei` | TEXT | 15-digit IMEI (required) |
| `imei2` | TEXT | Dual-SIM IMEI2 |
| `credits` | DECIMAL | Cost in credits |
| `status` | TEXT | Pending/Completed/Rejected/In Process |
| `carrier` | TEXT | **Result:** Carrier name |
| `simlock` | TEXT | **Result:** Lock status |
| `model` | TEXT | **Result:** Device model |
| `fmi` | TEXT | **Result:** Find My iPhone |
| `order_date` | TIMESTAMPTZ | When order was placed |
| `result_code` | TEXT | Raw CODE response |
| `result_code_display` | TEXT | Cleaned CODE for display |
| `notes` | TEXT | Additional notes |
| `raw_response` | TEXT | Full JSON response |
| `created_at` | TIMESTAMPTZ | Record created (auto) |
| `updated_at` | TIMESTAMPTZ | Last updated (auto) |

---

### `import_history` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-increment primary key |
| `filename` | TEXT | Name of imported CSV file |
| `rows_imported` | INTEGER | Number of successful imports |
| `rows_skipped` | INTEGER | Number of duplicates/errors |
| `import_date` | TIMESTAMPTZ | When import happened |

---

## How to Check Supabase Data

### Method 1: Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Select project: `opinemzfwtoduewqhqwp`
3. Click **Table Editor** → **orders**
4. See all your data in a spreadsheet view

---

### Method 2: Python

```python
from database_supabase import get_database

db = get_database()

# Get recent orders
orders = db.get_recent_orders(10)
for order in orders:
    print(f"IMEI: {order['imei']}, Status: {order['status']}")
```

---

### Method 3: Web Interface

```bash
python3 web_app.py
```

Visit: http://localhost:5001/history

See all orders in the web UI.

---

## Testing the Data Flow

### Test 1: Insert a Test Order

```bash
python3 << 'EOF'
import os
os.environ['SUPABASE_URL'] = 'https://opinemzfwtoduewqhqwp.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI'

from database_supabase import get_database
from datetime import datetime

db = get_database()

result = db.insert_order({
    'order_id': 'TEST-001',
    'imei': '123456789012345',
    'service_id': '1',
    'service_name': 'TEST ORDER',
    'status': 'Pending',
    'credits': 0.50,
    'order_date': datetime.now()
})

if result:
    print(f'✅ Test order inserted! ID: {result}')

    # Verify
    count = db.get_order_count()
    print(f'✅ Total orders in database: {count}')
else:
    print('❌ Failed to insert')
EOF
```

---

### Test 2: Query the Order

```bash
python3 << 'EOF'
import os
os.environ['SUPABASE_URL'] = 'https://opinemzfwtoduewqhqwp.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI'

from database_supabase import get_database

db = get_database()

orders = db.get_recent_orders(5)
print(f'Found {len(orders)} orders:')
for order in orders:
    print(f"  - {order['order_id']}: {order['imei']} ({order['status']})")
EOF
```

---

### Test 3: Update the Order

```bash
python3 << 'EOF'
import os
os.environ['SUPABASE_URL'] = 'https://opinemzfwtoduewqhqwp.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI'

from database_supabase import get_database

db = get_database()

db.update_order_status(
    order_id='TEST-001',
    status='Completed',
    result_code='SUCCESS',
    result_data={
        'carrier': 'T-Mobile',
        'model': 'iPhone 13',
        'simlock': 'Unlocked',
        'fmi': 'OFF'
    }
)

print('✅ Order updated to Completed')

# Verify
orders = db.get_orders_by_imei('123456789012345')
print(f'Order status: {orders[0]["status"]}')
print(f'Carrier: {orders[0]["carrier"]}')
print(f'Model: {orders[0]["model"]}')
EOF
```

---

## Production Usage

### Starting the Web App (with Supabase)

```bash
# Set environment variables
export SUPABASE_URL="https://opinemzfwtoduewqhqwp.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Start web app
python3 web_app.py
```

Or just run it - it reads from `.env` automatically:

```bash
python3 web_app.py
```

The system will:
1. ✅ Connect to Supabase automatically
2. ✅ Store all new orders in Supabase
3. ✅ Auto-sync every 5 minutes
4. ✅ Update orders with results

---

## Monitoring Data Flow

### Check Logs

```bash
tail -f web_app.log
```

Look for:
```
✓ Connected to Supabase: https://opinemzfwtoduewqhqwp.supabase.co
✓ Supabase connection verified
```

---

### Check Database

```python
from database_supabase import get_database

db = get_database()

# Summary
print(f"Total orders: {db.get_order_count()}")
print(f"Pending orders: {len(db.get_orders_by_status('Pending'))}")
print(f"Completed orders: {len(db.get_orders_by_status('Completed'))}")
```

---

## Data Flow Summary

### When You Submit an Order:

1. **Web Form** → `web_app.py` → `GSMFusionClient.place_imei_order()`
2. **API Response** → `database_supabase.insert_order()`
3. **Supabase** ← Order stored with status "Pending"

### When Order is Processed:

4. **Auto-Sync (5 min)** → `GSMFusionClient.get_imei_orders()`
5. **API Returns Results** → `database_supabase.update_order_status()`
6. **Supabase** ← Order updated with carrier, model, simlock, etc.

### Result:

✅ Order visible in Supabase dashboard
✅ Order visible in web interface
✅ Order searchable by IMEI
✅ Complete history preserved

---

## Common Questions

### Q: Where is data stored?
**A:** In Supabase PostgreSQL cloud database at `opinemzfwtoduewqhqwp.supabase.co`

### Q: Is it automatic?
**A:** Yes! Just run `python3 web_app.py` and it automatically uses Supabase.

### Q: Can I use both SQLite and Supabase?
**A:** System uses ONE at a time based on `.env`. Remove `SUPABASE_URL` to use SQLite.

### Q: How do I see the data?
**A:**
1. Supabase Dashboard → Table Editor
2. Web interface: http://localhost:5001/history
3. Python: `db.get_recent_orders()`

### Q: Is data synced automatically?
**A:** Yes, every 5 minutes the auto-sync updates pending orders.

### Q: Can I migrate from SQLite to Supabase?
**A:** Yes! Use `migrate_to_supabase.py` (already in your project).

---

## Next Steps

1. **Test the connection:**
   ```bash
   python3 -c "from database_supabase import get_database; print('Orders:', get_database().get_order_count())"
   ```

2. **Start the web app:**
   ```bash
   python3 web_app.py
   ```

3. **Submit a test order** via web interface

4. **Check Supabase dashboard** to see the data

---

**Status:** ✅ Supabase fully set up and ready to use!
**Current Orders:** 0
**Auto-Sync:** Enabled
**Web Interface:** Ready

🚀 **Your system is now collecting data in the cloud!**
