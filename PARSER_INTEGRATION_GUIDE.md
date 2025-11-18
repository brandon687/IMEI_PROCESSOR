# IMEI Data Parser → Supabase Integration Guide

## What This Does

Automatically parses the messy CODE field from GSM Fusion and populates clean columns in your Supabase database.

**Before:**
```
result_code: "Model: iPhone 13 128GB Midnight IMEI Number: 356825821305851..."
carrier: null
model: null
simlock: null
```

**After:**
```
result_code: "Model: iPhone 13 128GB Midnight IMEI Number: 356825821305851..."
carrier: "Unlocked"
model: "iPhone 13 128GB Midnight"
simlock: "Unlocked"
fmi: "OFF"
serial_number: "Y9WVV62WP9"
gsma_status: "Clean"
... (and 6 more fields!)
```

---

## Setup (One-Time, 5 Minutes)

### Step 1: Add Missing Columns to Supabase

1. **Go to Supabase SQL Editor:**
   - https://supabase.com/dashboard
   - Select project: **opinemzfwtoduewqhqwp**
   - Click **SQL Editor**

2. **Run this SQL:**

```sql
-- Add columns for parsed IMEI data
ALTER TABLE orders ADD COLUMN IF NOT EXISTS serial_number TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS meid TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS gsma_status TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS purchase_date TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS applecare TEXT;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tether_policy TEXT;
```

3. **Click "Run"**

---

### Step 2: Deploy Parser to Production

The parser files need to be on your production server:

```bash
# Add parser files to git
git add imei_data_parser.py auto_parse_orders.py add_parser_columns.sql

# Commit
git commit -m "Add IMEI data parser and auto-parse integration"

# Push to Railway
git push origin working-version-restore
```

Railway will auto-deploy.

---

## Usage

### Option 1: Parse All Existing Orders (One-Time)

Run this to parse all your existing completed orders:

```bash
python3 auto_parse_orders.py
```

**Output:**
```
🔍 AUTO-PARSE ORDERS - Populate Database Columns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Fetching orders from database...
Found 150 completed orders

[1/150] Processing order 12345678...
  ✓ Order 12345678: Updated 8 fields (model, carrier, simlock, fmi, ...)
[2/150] Processing order 12345679...
  ✓ Order 12345679: Updated 8 fields (model, carrier, simlock, fmi, ...)
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total orders processed: 150
  ✓ Successfully updated:  145
  ⊘ Skipped (no data):     3
  ✗ Failed:                2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Success! Check Supabase dashboard to see parsed columns.
```

---

### Option 2: Parse Only New/Unparsed Orders

If you've already run it once and just want to parse new orders:

```bash
python3 auto_parse_orders.py --new
```

This only parses orders that don't have model/carrier data yet.

---

### Option 3: Parse a Specific Order

```bash
python3 auto_parse_orders.py --order-id 12345678
```

---

### Option 4: Automatic Parsing (Recommended for Production)

Integrate into your auto-sync process. Add to `web_app.py`:

```python
# In web_app.py, add to auto_sync_orders() function

from imei_data_parser import IMEIDataParser

def auto_sync_orders():
    # ... existing sync code ...

    # After updating order status, parse the CODE
    parser = IMEIDataParser()

    for order in updated_orders:
        if order.get('result_code'):
            parsed = parser.parse(order['result_code'])

            # Update with parsed fields
            db.update_order_status(
                order_id=order['order_id'],
                status=order['status'],
                result_data={
                    'model': parsed.model,
                    'carrier': parsed.carrier,
                    'simlock': parsed.simlock,
                    'fmi': parsed.find_my_iphone,
                    # ... etc
                }
            )
```

---

## What Gets Parsed

The parser extracts these 12 fields from the CODE:

| Parser Field | Database Column | Example Value |
|--------------|----------------|---------------|
| `model` | `model` | "iPhone 13 128GB Midnight" |
| `imei_number` | `imei` | "356825821305851" |
| `serial_number` | `serial_number` | "Y9WVV62WP9" |
| `imei2_number` | `imei2` | "356825821314275" |
| `meid_number` | `meid` | "35682582130585" |
| `applecare_eligible` | `applecare` | "OFF" / "ON" |
| `estimated_purchase_date` | `purchase_date` | "02/10/21" |
| `carrier` | `carrier` | "Unlocked", "T-Mobile" |
| `next_tether_policy` | `tether_policy` | "10" |
| `current_gsma_status` | `gsma_status` | "Clean", "Blacklisted" |
| `find_my_iphone` | `fmi` | "OFF" / "ON" |
| `simlock` | `simlock` | "Unlocked", "Locked" |

---

## View Results in Supabase

After running the parser:

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard
   - Project: **opinemzfwtoduewqhqwp**

2. **Click "Table Editor"** → **"orders"**

3. **You'll now see populated columns:**
   - model
   - carrier
   - simlock
   - fmi
   - serial_number
   - meid
   - gsma_status
   - purchase_date
   - applecare
   - tether_policy

4. **Filter/Search by these columns:**
   - "Show me all Unlocked iPhones"
   - "Show me devices with FMI ON"
   - "Show me T-Mobile devices"

---

## Benefits

### Before Parser:
- ❌ All data stuck in one messy `result_code` field
- ❌ Can't filter by carrier
- ❌ Can't search by model
- ❌ Can't sort by lock status
- ❌ Hard to export clean data

### After Parser:
- ✅ Clean, searchable columns
- ✅ Filter by carrier: `WHERE carrier = 'T-Mobile'`
- ✅ Filter by lock: `WHERE simlock = 'Unlocked'`
- ✅ Filter by FMI: `WHERE fmi = 'OFF'`
- ✅ Export clean CSV with all columns
- ✅ Run SQL queries on parsed data
- ✅ Build dashboards/reports

---

## Testing

### Test with Sample Data

```bash
# Test locally first
export SUPABASE_URL="https://opinemzfwtoduewqhqwp.supabase.co"
export SUPABASE_KEY="eyJhbGci..."

# Run parser
python3 auto_parse_orders.py --new

# Check results
python3 -c "
from database_supabase import get_database
db = get_database()
orders = db.get_recent_orders(5)
for order in orders:
    print(f'{order[\"order_id\"]}: {order.get(\"model\", \"NO MODEL\")} - {order.get(\"carrier\", \"NO CARRIER\")}')
"
```

---

## Troubleshooting

### "No completed orders found"
- Check that you have orders with status = "Completed"
- Run: `python3 -c "from database_supabase import get_database; print(get_database().get_orders_by_status('Completed'))"`

### "Could not parse CODE"
- Check that orders have `result_code` or `result_code_display` field
- Check that the CODE contains data like "Model: iPhone..."

### "Database update failed"
- Verify Supabase connection: `python3 -c "from database_supabase import get_database; print(get_database().use_supabase)"`
- Check that columns exist in Supabase (run the ALTER TABLE SQL)

### Parser not recognizing fields
- The parser looks for patterns like "Model:", "Carrier:", etc.
- If your data format is different, you may need to update `HEADER_MAPPING` in `imei_data_parser.py`

---

## Production Integration

### Automatic Parsing on Sync

Update your auto-sync to automatically parse new orders:

```python
# In web_app.py or your sync script
from imei_data_parser import IMEIDataParser

parser = IMEIDataParser()

def sync_and_parse_order(order_id):
    # 1. Sync order status
    client = GSMFusionClient()
    result = client.get_imei_orders(order_id)

    # 2. Update database
    db.update_order_status(order_id, result['status'], result['CODE'])

    # 3. Parse the CODE immediately
    if result['CODE']:
        parsed = parser.parse(result['CODE'])
        db.update_order_status(
            order_id=order_id,
            status=result['status'],
            result_data=parsed.to_dict()
        )
```

---

## Scheduled Parsing (Cron Job)

Run parser every hour to catch any missed orders:

```bash
# Add to crontab
0 * * * * cd /path/to/HAMMER-API && python3 auto_parse_orders.py --new >> /tmp/parser.log 2>&1
```

---

## Summary

**What you get:**
- 12 clean, searchable columns in Supabase
- Automatic parsing of messy CODE data
- Easy filtering and reporting
- Clean CSV exports

**Files involved:**
- `imei_data_parser.py` - The parser (already created)
- `auto_parse_orders.py` - Integration script (just created)
- `add_parser_columns.sql` - Schema updates (just created)

**Next steps:**
1. Run SQL to add columns to Supabase
2. Run `python3 auto_parse_orders.py` to parse existing orders
3. Check Supabase to see populated columns
4. Enjoy clean, searchable data!

---

**Created:** 2025-11-18
**Status:** Ready to use
**Dependencies:** `imei_data_parser.py` (already in project)
