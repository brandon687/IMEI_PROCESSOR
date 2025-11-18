# Manual Sync & Parse - Quick Start Guide

**For Production Use** 🚀

---

## What It Does

Automatically syncs pending orders from GSM Fusion API and extracts 12+ fields from the response:

- Model, Carrier, SIM Lock, Find My iPhone
- Serial Number, IMEI2, MEID
- GSMA Status, Purchase Date, AppleCare, Tether Policy

---

## How to Use

### Option 1: Web Interface (Recommended)

1. Navigate to `/database` page
2. Click **"🔄 Manual Sync & Parse Orders"** button
3. Wait for completion (shows progress)
4. View sample parsed data in alert
5. Page auto-refreshes to show updated data

### Option 2: API Call

```bash
curl -X POST http://localhost:5001/manual-sync \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "parse=true"
```

Response:
```json
{
  "success": true,
  "stats": {
    "total_pending": 10,
    "synced": 10,
    "completed": 8,
    "parsed": 8,
    "parse_failures": 0
  },
  "sample_parsed": [...]
}
```

---

## What Gets Parsed

From this text in CODE field:
```
Model: iPhone 13 128GB Midnight
IMEI Number: 356825821305851
Serial Number: Y9WVV62WP9
IMEI2 Number: 356825821314275
MEID Number: 35682582130585
AppleCare Eligible: OFF
Estimated Purchase Date: 02/10/21
Carrier: Unlocked
Next Tether Policy: 10
Current GSMA Status: Clean
Find My iPhone: OFF
SimLock: Unlocked
```

To these database columns:
- `model` → "iPhone 13 128GB Midnight"
- `carrier` → "Unlocked"
- `simlock` → "Unlocked"
- `fmi` → "OFF"
- `serial_number` → "Y9WVV62WP9"
- `imei2` → "356825821314275"
- `meid` → "35682582130585"
- `gsma_status` → "Clean"
- `purchase_date` → "02/10/21"
- `applecare` → "OFF"
- `tether_policy` → "10"

---

## Typical Results

For **10 pending orders**:
- ⏱️ Duration: ~3-5 seconds
- ✅ Synced: 10
- ✅ Completed: 8 (status updated to Completed)
- ✅ Parsed: 8 (data extracted and stored)
- ❌ Parse Failures: 0

---

## When to Use

1. **After submitting IMEIs**: Orders start as "Pending"
2. **To check status**: Updates from Pending → Completed
3. **To extract data**: Parses CODE field into structured columns
4. **For CSV export**: Export with all parsed fields

---

## Files Modified

1. ✅ `database.py` - Added 6 new columns
2. ✅ `web_app.py` - Added `/manual-sync` route
3. ✅ `templates/database.html` - Added button + JavaScript

---

## Troubleshooting

### No Pending Orders
- Message: "No pending orders to sync"
- Solution: Submit some orders first at `/submit`

### Parse Failures
- Check `web_app.log` for details
- View raw CODE: `SELECT result_code FROM orders WHERE order_id = 'X'`
- Report edge cases for improvement

### API Timeout
- Increase timeout in code (default: 60s)
- Check GSM Fusion API status
- Try smaller batches

---

## Monitoring

Watch logs for:
```
=== MANUAL SYNC & PARSE STARTED ===
Found X pending orders to sync
API returned X orders in X.XXs
✓ Parsed X fields: [...]
✓ Updated order X with parsed data
=== MANUAL SYNC & PARSE FINISHED in X.XXs ===
```

Enable debug mode:
```bash
LOG_LEVEL=DEBUG python3 web_app.py
```

---

## Performance

| Orders | Duration | Notes           |
|--------|----------|-----------------|
| 10     | ~3s      | Typical batch   |
| 50     | ~5s      | Large batch     |
| 100    | ~7s      | Max recommended |

---

## Next Steps

1. Submit orders via `/submit` or `/batch`
2. Wait for orders to process (1-5 minutes)
3. Click "Manual Sync & Parse Orders"
4. Export data via CSV with parsed fields

---

**Full Documentation**: See `MANUAL_SYNC_PARSER_FEATURE.md`
