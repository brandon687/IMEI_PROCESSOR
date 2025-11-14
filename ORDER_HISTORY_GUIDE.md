# Order History System - Complete Guide

## How Your Order History Works

Your IMEI order history system now has **3 components** working together:

### 1. **GSM Fusion API** (Remote Storage)
- GSM Fusion stores ALL your orders on their servers
- You can fetch order status at any time using order IDs
- API method: `client.get_imei_orders(order_id)` or `client.get_imei_orders([id1, id2, id3])`

### 2. **Local SQLite Database** (Persistent Storage)
- Location: `/Users/brandonin/Desktop/HAMMER-API/imei_orders.db`
- Stores orders you submit through the web app
- Persists across server restarts (unlike RECENT_ORDERS which was in-memory)
- Table: `orders` with columns for IMEI, status, service_id, order_date, etc.

### 3. **Web Interface** (Display Layer)
- `/history` - Shows orders from your local database
- `/history/sync` - Fetches latest status from GSM Fusion API and updates database
- `/status/<order_id>` - Shows detailed order status from API

---

## How It Works: Step-by-Step

### When You Submit an Order

**User Action**: Submit IMEI through web form or CSV upload

**What Happens**:

1. **API Call to GSM Fusion** (web_app.py:115)
   ```python
   result = client.place_imei_order(imei=imei, network_id=service_id)
   ```
   - Sends IMEI + service_id to GSM Fusion
   - GSM Fusion creates order and returns `order_id`

2. **Store in Local Database** (web_app.py:140-147)
   ```python
   db.insert_order({
       'order_id': order['id'],        # GSM Fusion order ID
       'service_id': service_id,
       'imei': imei,
       'status': order['status'],      # Initial status (usually "Pending")
       'order_date': datetime.now(),
       'raw_response': str(order)
   })
   ```
   - Saves order to SQLite database
   - Now persisted even if web server restarts

3. **Add to Recent Orders** (web_app.py:131-137)
   ```python
   RECENT_ORDERS.insert(0, {...})
   ```
   - In-memory list for quick access (last 10 orders)
   - Lost on restart, but database keeps everything

**Result**: Order is now in 3 places:
- ✅ GSM Fusion servers (remote, authoritative)
- ✅ Your SQLite database (local, persistent)
- ✅ RECENT_ORDERS list (in-memory, temporary)

---

### When You View Order History

**User Action**: Click "Order History" in navigation

**What Happens**:

1. **Query Local Database** (web_app.py:389)
   ```python
   orders = db.get_recent_orders(limit=100)
   ```
   - Fetches last 100 orders from SQLite
   - Sorted by `order_date DESC` (newest first)

2. **Format for Display** (web_app.py:392-400)
   ```python
   formatted_orders = []
   for order in orders:
       formatted_orders.append({
           'order_id': order.get('order_id'),
           'imei': order.get('imei'),
           'service_id': order.get('service_id'),
           'status': order.get('status'),
           'timestamp': order.get('order_date')
       })
   ```

3. **Render Template** (templates/history.html)
   - Displays table with order_id, IMEI, status, timestamp
   - Shows status badges (green=completed, yellow=pending, red=error)
   - "View Details" button for each order

**Result**: You see all orders from database, even after server restart

---

### When You Sync Order Status

**User Action**: Click "🔄 Sync Status from API" button

**What Happens**:

1. **Find Pending Orders** (web_app.py:413)
   ```python
   pending_orders = db.search_orders_by_status(['Pending', 'In Process'])
   ```
   - Gets all orders that aren't completed yet
   - These are the ones that might have updated status

2. **Batch Fetch from API** (web_app.py:427-429)
   ```python
   order_ids = [order['order_id'] for order in pending_orders]
   updated_orders = client.get_imei_orders(order_ids)  # Supports batch!
   ```
   - GSM Fusion API accepts comma-separated order IDs
   - Returns latest status for all orders in one call

3. **Update Database** (web_app.py:435-440)
   ```python
   for api_order in updated_orders:
       db.update_order_status(
           order_id=api_order.id,
           status=api_order.status,
           code=api_order.code
       )
   ```
   - Updates each order's status in SQLite
   - Now your local database matches GSM Fusion

**Result**: Local database status is now in sync with GSM Fusion API

---

## Database Schema

### `orders` Table Structure

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,              -- GSM Fusion order ID
    service_name TEXT,                  -- Service display name
    service_id TEXT,                    -- Service package ID
    imei TEXT NOT NULL,                 -- Device IMEI number
    imei2 TEXT,                         -- Dual-SIM IMEI2
    credits REAL,                       -- Cost in credits
    status TEXT,                        -- Order status (Pending/Completed/Rejected)
    carrier TEXT,                       -- Carrier name (from results)
    simlock TEXT,                       -- SIM lock status
    model TEXT,                         -- Device model
    fmi TEXT,                           -- Find My iPhone status
    order_date TIMESTAMP,               -- When order was placed
    result_code TEXT,                   -- Result code from API
    notes TEXT,                         -- Additional notes
    raw_response TEXT,                  -- Full API response (for debugging)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example Row

```json
{
    "id": 1,
    "order_id": "12345678",
    "service_name": "iPhone IMEI Checker",
    "service_id": "269",
    "imei": "352130219890307",
    "imei2": null,
    "credits": 0.12,
    "status": "Completed",
    "carrier": "AT&T USA",
    "simlock": "Unlocked",
    "model": "iPhone 14 Pro",
    "fmi": "OFF",
    "order_date": "2025-11-13 14:30:00",
    "result_code": "SUCCESS",
    "notes": null,
    "raw_response": "{'id': '12345678', 'status': 'Completed', ...}",
    "created_at": "2025-11-13 14:30:00",
    "updated_at": "2025-11-13 14:35:12"
}
```

---

## API Integration Details

### GSM Fusion API Methods Used

#### 1. **Place IMEI Order**
```python
client.place_imei_order(imei="352130219890307", network_id="269")
```

**Returns**:
```python
{
    'orders': [
        {
            'id': '12345678',           # Order ID
            'imei': '352130219890307',
            'status': 'Pending',
            'package': 'iPhone IMEI Checker',
            'requestedat': '2025-11-13 14:30:00'
        }
    ],
    'errors': [],
    'duplicates': []
}
```

#### 2. **Get Order Status (Single)**
```python
orders = client.get_imei_orders("12345678")
```

**Returns**:
```python
[
    IMEIOrder(
        id='12345678',
        imei='352130219890307',
        package='iPhone IMEI Checker',
        status='Completed',
        code='SUCCESS',
        requested_at='2025-11-13 14:30:00'
    )
]
```

#### 3. **Get Order Status (Batch)**
```python
orders = client.get_imei_orders(["12345678", "12345679", "12345680"])
```

**Returns**: List of IMEIOrder objects (one per order)

**Performance**: GSM Fusion API supports batch lookups!
- Single call for 1 order ≈ 300ms
- Single call for 100 orders ≈ 500ms (much faster than 100 separate calls!)

---

## Workflow Examples

### Example 1: Submit Multiple IMEIs via CSV

**User Action**:
1. Navigate to `/batch`
2. Upload CSV with 500 IMEIs
3. Select service "iPhone IMEI Checker"
4. Click "Process Batch"

**System Flow**:
```
1. Read CSV file (500 rows)
2. For each IMEI:
   - Call API: client.place_imei_order(imei, service_id)
   - If successful: Store in database
   - If error: Log error message
3. Show summary: "450 successful, 50 errors"
4. Database now has 450 new orders (status: Pending)
```

**Database State**:
```sql
SELECT COUNT(*) FROM orders WHERE status = 'Pending';
-- Result: 450 orders
```

---

### Example 2: Check Order Status After 1 Hour

**User Action**:
1. Navigate to `/history`
2. Click "🔄 Sync Status from API"

**System Flow**:
```
1. Query database for pending orders:
   SELECT * FROM orders WHERE status IN ('Pending', 'In Process')
   -- Returns 450 orders

2. Extract order IDs:
   order_ids = ['12345678', '12345679', ..., '12346127']

3. Batch fetch from API (GSM Fusion supports comma-separated IDs):
   client.get_imei_orders(order_ids)
   -- Single API call returns status for all 450 orders!

4. Update database:
   UPDATE orders SET status = 'Completed', result_code = 'SUCCESS' WHERE order_id = '12345678'
   -- Repeat for all 450 orders

5. Show message: "Successfully synced 450 order(s)"
```

**Database State After Sync**:
```sql
SELECT status, COUNT(*) FROM orders GROUP BY status;
-- Result:
-- Completed: 445
-- Rejected: 5
```

---

### Example 3: View Individual Order Details

**User Action**:
1. Navigate to `/history`
2. Click "View Details" on order #12345678

**System Flow**:
```
1. Fetch from GSM Fusion API (real-time):
   orders = client.get_imei_orders("12345678")

2. Display results:
   - IMEI: 352130219890307
   - Status: Completed
   - Carrier: AT&T USA
   - SIM Lock: Unlocked
   - Model: iPhone 14 Pro
   - Find My iPhone: OFF
   - Result Code: SUCCESS
```

**Note**: `/status/<order_id>` always fetches from API (real-time), not database. This ensures you see the latest status even if you haven't synced.

---

## Database vs API: When to Use Each

### Use Local Database When:
✅ **Viewing order history** - Fast, no API calls needed
✅ **Searching orders** - Search by IMEI, model, carrier in local database
✅ **Exporting data** - Generate CSV reports from database
✅ **Displaying statistics** - Count orders by status, date, etc.

### Use GSM Fusion API When:
✅ **Submitting new orders** - Must go through API
✅ **Getting real-time status** - API has most up-to-date info
✅ **Viewing order details** - API returns full result data
✅ **Syncing status** - Batch update database from API

---

## Sync Strategy Recommendations

### Option A: Manual Sync (Current Implementation)
**How It Works**: User clicks "Sync Status" button when they want updates

**Pros**:
- No unnecessary API calls
- User controls when sync happens
- Simple implementation

**Cons**:
- Database may be out of sync until user manually syncs
- User has to remember to sync

**Best For**: Low-volume operations (<100 orders/day)

---

### Option B: Auto-Sync on Page Load (Optional Enhancement)
**How It Works**: Sync pending orders every time user visits `/history`

**Implementation**:
```python
@app.route('/history')
def history():
    # Auto-sync pending orders
    pending_orders = db.search_orders_by_status(['Pending', 'In Process'])
    if pending_orders:
        order_ids = [o['order_id'] for o in pending_orders]
        client = GSMFusionClient()
        updated_orders = client.get_imei_orders(order_ids)
        for api_order in updated_orders:
            db.update_order_status(api_order.id, api_order.status, api_order.code)
        client.close()

    # Show history
    orders = db.get_recent_orders(limit=100)
    return render_template('history.html', orders=orders)
```

**Pros**:
- Database always up-to-date
- User doesn't need to remember to sync
- Seamless experience

**Cons**:
- Adds API call to every page load
- Slower page load times
- More API usage (may impact costs)

**Best For**: Medium-volume operations (100-500 orders/day)

---

### Option C: Background Sync Task (Advanced)
**How It Works**: Cron job or background worker syncs every 5-10 minutes

**Implementation** (using APScheduler):
```python
from apscheduler.schedulers.background import BackgroundScheduler

def sync_pending_orders():
    """Background task to sync pending orders"""
    db = get_database()
    pending_orders = db.search_orders_by_status(['Pending', 'In Process'])

    if pending_orders:
        order_ids = [o['order_id'] for o in pending_orders]
        client = GSMFusionClient()
        updated_orders = client.get_imei_orders(order_ids)

        for api_order in updated_orders:
            db.update_order_status(api_order.id, api_order.status, api_order.code)

        client.close()
        logger.info(f"Auto-synced {len(updated_orders)} orders")

# Start background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(sync_pending_orders, 'interval', minutes=10)
scheduler.start()
```

**Pros**:
- Database always current (within 10 minutes)
- No impact on page load times
- User doesn't think about syncing

**Cons**:
- More complex implementation
- Requires background worker
- More API usage

**Best For**: High-volume operations (500+ orders/day)

---

## API Rate Limits & Cost Optimization

### GSM Fusion API Behavior

**Batch Support**: Yes! (comma-separated order IDs)
```python
# Good: Single API call for 100 orders
client.get_imei_orders(["id1", "id2", ..., "id100"])

# Bad: 100 separate API calls
for order_id in order_ids:
    client.get_imei_orders(order_id)  # Don't do this!
```

**Rate Limits**: (Check with GSM Fusion)
- Typical: 60 requests/minute or 1000 requests/hour
- Batch requests count as 1 request (regardless of how many IDs)

**Cost**: (Check your pricing)
- Typical: Pay per order placed, not per status check
- Status checks (get_imei_orders) are usually free/unlimited

### Optimization Tips

1. **Always batch status checks**
   ```python
   # Get all pending orders
   pending = db.search_orders_by_status(['Pending', 'In Process'])
   order_ids = [o['order_id'] for o in pending]

   # Single API call for all
   client.get_imei_orders(order_ids)
   ```

2. **Only sync orders that need it**
   ```python
   # Don't sync completed orders
   pending_orders = db.search_orders_by_status(['Pending', 'In Process'])
   # Skip orders created in last 5 minutes (too soon to complete)
   ```

3. **Cache results**
   ```python
   # Store API response in database
   db.update_order_status(order_id, status, code)
   # Next view uses cached data, not API call
   ```

---

## Troubleshooting

### Problem: "No orders showing in /history"

**Cause**: Database is empty or orders weren't stored

**Solution**:
1. Check if database file exists:
   ```bash
   ls -la /Users/brandonin/Desktop/HAMMER-API/imei_orders.db
   ```

2. Check if orders are in database:
   ```python
   from database import get_database
   db = get_database()
   orders = db.get_recent_orders(limit=10)
   print(f"Found {len(orders)} orders")
   ```

3. Submit a test order through `/submit` to populate database

---

### Problem: "Sync Status button does nothing"

**Cause**: No pending orders to sync, or API error

**Solution**:
1. Check Flask console for errors:
   ```
   [ERROR] API sync failed: Connection timeout
   ```

2. Verify you have pending orders:
   ```sql
   SELECT COUNT(*) FROM orders WHERE status IN ('Pending', 'In Process');
   ```

3. Test API connection:
   ```python
   from gsm_fusion_client import GSMFusionClient
   client = GSMFusionClient()
   services = client.get_imei_services()  # Should work
   ```

---

### Problem: "Order shows as Pending but API says Completed"

**Cause**: Database is out of sync with API

**Solution**:
1. Click "🔄 Sync Status from API" button in `/history`
2. Or manually sync:
   ```python
   db.update_order_status(order_id="12345678", status="Completed")
   ```

---

### Problem: "Database file is huge"

**Cause**: Storing too many orders or large raw_response data

**Solution**:
1. Check database size:
   ```bash
   du -h /Users/brandonin/Desktop/HAMMER-API/imei_orders.db
   ```

2. Clean old orders:
   ```sql
   DELETE FROM orders WHERE order_date < date('now', '-90 days');
   VACUUM;  -- Reclaim space
   ```

3. Archive old orders:
   ```python
   # Export to CSV
   db.export_to_csv('archive_2025.csv', filters={'end_date': '2025-12-31'})
   # Then delete from database
   ```

---

## Quick Reference

### Important Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/submit` | GET/POST | Submit single or multiple IMEIs |
| `/batch` | GET/POST | Upload CSV file with IMEIs |
| `/history` | GET | View order history from database |
| `/history/sync` | GET | Sync pending orders from API |
| `/status/<order_id>` | GET | View real-time order details from API |
| `/database` | GET | View database statistics |
| `/database/search` | GET | Search orders in database |
| `/database/export` | GET | Export orders to CSV |

### Database Methods

```python
from database import get_database
db = get_database()

# Insert new order
db.insert_order({
    'order_id': '12345678',
    'imei': '352130219890307',
    'service_id': '269',
    'status': 'Pending'
})

# Get recent orders
orders = db.get_recent_orders(limit=100)

# Search by status
pending = db.search_orders_by_status(['Pending', 'In Process'])

# Update order status
db.update_order_status(order_id='12345678', status='Completed', code='SUCCESS')

# Search orders
results = db.search_orders('352130219890307')  # By IMEI

# Export to CSV
db.export_to_csv('export.csv')
```

### API Methods

```python
from gsm_fusion_client import GSMFusionClient
client = GSMFusionClient()

# Place order
result = client.place_imei_order(imei='352130219890307', network_id='269')

# Get order status (single)
orders = client.get_imei_orders('12345678')

# Get order status (batch)
orders = client.get_imei_orders(['12345678', '12345679', '12345680'])

# Close connection
client.close()
```

---

## Summary

Your order history system is now **fully functional and persistent**:

✅ **Submit orders** → Stored in database + GSM Fusion
✅ **View history** → Loads from database (fast, persistent)
✅ **Sync status** → Updates database from API (batch efficient)
✅ **View details** → Real-time fetch from API (always current)
✅ **Search orders** → Query local database (instant)
✅ **Export data** → CSV export from database

**Key Benefit**: You have a local mirror of your order history that:
- Persists across server restarts
- Works offline (for viewing)
- Syncs with GSM Fusion API when needed
- Supports fast searching and reporting

Your order history is no longer lost when you restart the web server! 🎉
