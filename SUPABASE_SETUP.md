# Supabase Setup Guide for HAMMER-API

## Why Supabase?

Supabase provides:
- **99.9% uptime** - Enterprise-grade PostgreSQL hosting
- **Automatic backups** - Daily backups with point-in-time recovery
- **Real-time updates** - Optional real-time subscriptions
- **Scalability** - Handles millions of rows effortlessly
- **Free tier** - 500MB database, 2GB storage, 50K MAU
- **Built-in API** - Auto-generated REST and GraphQL APIs

Perfect for production IMEI processing with 6,000-20,000 daily orders.

---

## Quick Start (5 Minutes)

### Step 1: Create Supabase Project

1. Go to https://app.supabase.com
2. Sign up/login (free account)
3. Click **"New Project"**
4. Fill in:
   - **Name**: `hammer-api` or `imei-processor`
   - **Database Password**: Generate strong password (save it!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
5. Click **"Create new project"**
6. Wait ~2 minutes for provisioning

### Step 2: Create Database Tables

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy the entire contents of `supabase_schema.sql` from this repo
4. Paste into SQL editor
5. Click **"Run"** (or press Ctrl+Enter)
6. You should see: "Success. No rows returned"

### Step 3: Get Your Credentials

1. In Supabase dashboard, go to **Settings** (gear icon) → **API**
2. Copy these two values:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public key**: `eyJhbGc...` (long string)

**Important**: Use the **anon** key (or **service_role** key for backend-only access).

### Step 4: Configure Environment Variables

#### For Local Development

Create `.env` file in project root:
```bash
# GSM Fusion API
GSM_FUSION_API_KEY=your-gsm-fusion-key
GSM_FUSION_USERNAME=your-username
GSM_FUSION_BASE_URL=http://hammerfusion.com

# Supabase (paste your credentials here)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional
LOG_LEVEL=INFO
AUTO_SYNC_INTERVAL=300
```

#### For Railway Deployment

1. Go to Railway dashboard: https://railway.app
2. Select your `IMEI-PROCESSOR` project
3. Click **"Variables"** tab
4. Add these environment variables:
   ```
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   GSM_FUSION_API_KEY=your-key
   GSM_FUSION_USERNAME=your-username
   GSM_FUSION_BASE_URL=http://hammerfusion.com
   ```
5. Click **"Deploy"** to restart with new variables

---

## Verification

### Test Connection Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test database connection
python3 -c "from database import get_database; db = get_database(); print('✓ Connected to Supabase!')"
```

If successful, you'll see: `✓ Connected to Supabase!`

### Start Web Interface

```bash
python3 web_app.py
```

Visit http://localhost:5001 and:
1. Submit a test IMEI order
2. Check **Order History** - should show in database
3. Verify in Supabase dashboard → **Table Editor** → **orders**

---

## Supabase Dashboard Tour

### Key Features

1. **Table Editor**
   - View/edit orders directly
   - Search and filter data
   - Export to CSV

2. **SQL Editor**
   - Run custom queries
   - Create indexes
   - Analyze performance

3. **Database → Backups**
   - Automatic daily backups (paid plans)
   - Point-in-time recovery
   - Manual backup download

4. **Logs**
   - Query performance logs
   - Error tracking
   - API usage monitoring

5. **Settings → API**
   - View/rotate API keys
   - Check usage limits
   - Connection strings

---

## Schema Details

### `orders` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-increment primary key |
| `order_id` | TEXT | Unique GSM Fusion order ID |
| `service_name` | TEXT | Service display name |
| `service_id` | TEXT | Service package ID |
| `imei` | TEXT | 15-digit IMEI number |
| `imei2` | TEXT | Secondary IMEI (dual-SIM) |
| `credits` | DECIMAL | Cost in credits |
| `status` | TEXT | Pending/Completed/Rejected/In Process |
| `carrier` | TEXT | Carrier name (result) |
| `simlock` | TEXT | Lock status (result) |
| `model` | TEXT | Device model (result) |
| `fmi` | TEXT | Find My iPhone status |
| `order_date` | TIMESTAMPTZ | When order was placed |
| `result_code` | TEXT | Raw CODE with HTML tags |
| `result_code_display` | TEXT | Cleaned CODE for display |
| `notes` | TEXT | Additional information |
| `raw_response` | TEXT | Full JSON from API |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

### Indexes (for performance)

- `idx_orders_imei` - Fast IMEI lookups
- `idx_orders_order_id` - Fast order ID lookups
- `idx_orders_order_date` - Chronological sorting
- `idx_orders_status` - Status filtering
- `idx_orders_created_at` - Recent orders

### `import_history` Table

Tracks bulk imports from CSV/Excel files.

---

## Common Operations

### Query Orders in SQL Editor

```sql
-- Recent 10 orders
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;

-- Pending orders
SELECT * FROM orders WHERE status = 'Pending';

-- Orders by IMEI
SELECT * FROM orders WHERE imei = '123456789012345';

-- Today's orders
SELECT COUNT(*) FROM orders WHERE order_date::date = CURRENT_DATE;

-- Total credits spent
SELECT SUM(credits) FROM orders WHERE credits IS NOT NULL;

-- Orders by status breakdown
SELECT status, COUNT(*) as count, SUM(credits) as total_credits
FROM orders
GROUP BY status
ORDER BY count DESC;
```

### Export Data

**Via Dashboard:**
1. Table Editor → orders
2. Filter if needed
3. Click "Export" → CSV

**Via Code:**
```python
from database import get_database

db = get_database()
db.export_to_csv('export.csv', filters={'status': 'Completed'})
```

---

## Security Best Practices

### Row Level Security (RLS)

The schema enables RLS by default:
- **service_role** key has full access (use in backend)
- **anon** key respects RLS policies
- Public users have no access (unless you create policies)

### Recommended Key Usage

**For Backend/Railway:**
- Use **service_role** key (full access)
- Keep it secret in environment variables
- Never expose in frontend code

**For Frontend (if building one):**
- Use **anon** key (limited access)
- Create custom RLS policies for user access
- Safe to expose in browser

### Rotating Keys

If compromised:
1. Supabase Dashboard → Settings → API
2. Click "Rotate" next to compromised key
3. Update environment variables everywhere
4. Redeploy apps

---

## Pricing & Limits

### Free Tier (Sufficient for Testing)
- **Database**: 500 MB
- **Storage**: 1 GB
- **API Requests**: Unlimited (rate limited)
- **Bandwidth**: 2 GB/month

**Estimated capacity:**
- ~50,000 orders (10KB each)
- 5,000-10,000 orders/day for testing

### Pro Tier ($25/month)
- **Database**: 8 GB (expandable)
- **Storage**: 100 GB
- **Daily backups**
- **Point-in-time recovery**
- **Bandwidth**: 250 GB/month

**Estimated capacity:**
- ~800,000 orders
- 20,000-50,000 orders/day production use

### Scale to Millions
- Database scales to 1TB+
- Automatic read replicas
- Custom plans available

---

## Monitoring & Maintenance

### Check Database Size

```sql
SELECT pg_size_pretty(pg_database_size(current_database()));
```

### Monitor Table Growth

```sql
SELECT
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### Clean Old Data (Optional)

```sql
-- Delete orders older than 1 year
DELETE FROM orders WHERE order_date < NOW() - INTERVAL '1 year';

-- Archive old orders to separate table
CREATE TABLE orders_archive AS
SELECT * FROM orders WHERE order_date < NOW() - INTERVAL '1 year';

DELETE FROM orders WHERE order_date < NOW() - INTERVAL '1 year';
```

---

## Migration from SQLite

If you have existing SQLite data:

### Option 1: Manual Import via Web UI

1. Export SQLite to CSV:
   ```python
   from database import get_database
   db = get_database()
   db.export_to_csv('old_orders.csv')
   ```

2. In Supabase Dashboard → Table Editor → orders
3. Click "Insert" → "Import data from CSV"
4. Upload `old_orders.csv`

### Option 2: Python Script

```python
import sqlite3
from database import get_database

# Connect to old SQLite database
old_conn = sqlite3.connect('imei_orders.db')
old_conn.row_factory = sqlite3.Row
cursor = old_conn.cursor()

# Get new Supabase database
new_db = get_database()

# Migrate data
cursor.execute('SELECT * FROM orders')
for row in cursor.fetchall():
    order_data = dict(row)
    new_db.insert_order(order_data)
    print(f"Migrated order: {order_data['order_id']}")

old_conn.close()
print("Migration complete!")
```

---

## Troubleshooting

### Error: "Missing Supabase credentials"

**Cause**: Environment variables not set
**Fix**:
```bash
export SUPABASE_URL=https://xxxxx.supabase.co
export SUPABASE_KEY=eyJhbGciOi...
```

### Error: "relation 'orders' does not exist"

**Cause**: Tables not created
**Fix**: Run `supabase_schema.sql` in SQL Editor

### Error: "permission denied for table orders"

**Cause**: Using anon key without RLS policy
**Fix**: Use service_role key for backend, or create RLS policy

### Slow Queries

**Cause**: Missing indexes or large dataset
**Fix**:
1. Check indexes exist: `\d orders` in SQL Editor
2. Analyze query: `EXPLAIN ANALYZE SELECT ...`
3. Add indexes for common filters

### Connection Timeout

**Cause**: Network issues or Supabase outage
**Fix**:
1. Check Supabase status: https://status.supabase.com
2. Verify SUPABASE_URL is correct
3. Check firewall/network settings

---

## Performance Tips

### Use Indexes

Already created by schema, but verify:
```sql
-- Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'orders';
```

### Batch Inserts

Instead of 1000 individual inserts:
```python
# Good: Batch insert
data = [{'order_id': 'xxx', ...}, ...]
response = client.table('orders').insert(data).execute()
```

### Connection Pooling

Supabase handles this automatically. No configuration needed.

### Query Optimization

```python
# Bad: Fetch all, filter in Python
all_orders = db.get_recent_orders(limit=10000)
pending = [o for o in all_orders if o['status'] == 'Pending']

# Good: Filter in database
pending = db.get_orders_by_status('Pending')
```

---

## Support Resources

### Supabase
- **Documentation**: https://supabase.com/docs
- **Discord**: https://discord.supabase.com
- **Status**: https://status.supabase.com
- **Support**: team@supabase.io

### HAMMER-API
- **GitHub**: https://github.com/brandon687/IMEI_PROCESSOR
- **Issues**: https://github.com/brandon687/IMEI_PROCESSOR/issues

---

## Summary Checklist

Before going live:

- [ ] Supabase project created
- [ ] Tables created via `supabase_schema.sql`
- [ ] Credentials added to Railway environment variables
- [ ] Test order submitted successfully
- [ ] Order appears in Supabase Table Editor
- [ ] Auto-sync working (check logs)
- [ ] Backups enabled (Pro plan recommended)
- [ ] Monitor database size regularly

---

## Next Steps

1. **Test thoroughly** - Submit orders and verify in Supabase
2. **Monitor usage** - Check Supabase dashboard daily
3. **Enable backups** - Upgrade to Pro if handling real data
4. **Set alerts** - Configure email alerts for high usage
5. **Scale as needed** - Upgrade plan when approaching limits

Your HAMMER-API is now production-ready with enterprise-grade PostgreSQL! 🚀
