# Batch Submission Debug - 3 IMEIs Issue

## Problem

Submitted 3 IMEIs but only 1 showing in order history:
- IMEI 1: 356967067494955
- IMEI 2: 356942282539686  
- IMEI 3: 355804085587570

**Expected**: All 3 orders in database
**Actual**: Only the last IMEI (355804085587570) appears

---

## What We Added

**Enhanced Logging** (Commit `e724c4a`):
- Logs total number of orders being stored
- Logs each order before insertion with order_id and IMEI
- Logs success message after each insertion
- Logs full error traceback if insertion fails

---

## Testing on Railway

### Step 1: Deploy New Version
Railway is deploying now (2-3 minutes)

### Step 2: Submit Test IMEIs
1. Go to Railway URL → `/submit`
2. Enter these 3 test IMEIs (one per line):
   ```
   111111111111111
   222222222222222
   333333333333333
   ```
3. Select a service
4. Click Submit

### Step 3: Check Railway Logs
Go to Railway dashboard → Deployments → View Logs

**Look for**:
```
Storing 3 orders in database
Inserting order 1/3: order_id=XXXXX, imei=111111111111111
✓ Successfully inserted order XXXXX
Inserting order 2/3: order_id=YYYYY, imei=222222222222222
✓ Successfully inserted order YYYYY
Inserting order 3/3: order_id=ZZZZZ, imei=333333333333333
✓ Successfully inserted order ZZZZZ
```

**If you see errors**:
```
❌ DB insert failed for order XXXXX: UNIQUE constraint failed: orders.order_id
```

This would tell us if there's a duplicate order_id issue.

---

## Possible Causes

### 1. Duplicate Order IDs
If GSM Fusion API returns the same order_id for multiple IMEIs, the UNIQUE constraint would block subsequent inserts.

**Fix**: Change order_id to non-unique, or use composite key (order_id + imei)

### 2. Database Connection Issues
If database connection drops between inserts, only some orders would save.

**Fix**: Wrap inserts in transaction

### 3. API Response Parsing
If API returns orders in unexpected format, we might only parse 1.

**Fix**: Log the raw response structure

---

## Quick Checks

### Check Current Orders
```bash
# On Railway, open shell and run:
sqlite3 imei_orders.db "SELECT order_id, imei, status FROM orders ORDER BY created_at DESC LIMIT 10"
```

### Check for Duplicates
```bash
sqlite3 imei_orders.db "SELECT order_id, COUNT(*) as count FROM orders GROUP BY order_id HAVING count > 1"
```

---

## Next Steps

1. **Wait for Railway deployment** (2-3 minutes)
2. **Submit 3 test IMEIs** (fresh ones, not previously used)
3. **Check Railway logs** for the detailed output
4. **Report what you see** - we'll fix based on the logs

---

## Temporary Workaround

If you need all 3 orders tracked NOW:
1. Submit each IMEI individually (one at a time)
2. This ensures each gets its own order_id
3. Then we can fix the batch submission

---

## Related Issues to Fix

### Sync Status Not Working
The sync button should update pending orders from Hammer. We'll tackle this after fixing batch submission.

### Supabase Empty
Database tables might not be created yet. Need to run schema SQL in Supabase dashboard.

