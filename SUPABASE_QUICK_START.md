# Supabase Setup - Quick Start Guide

**Status**: Ready to deploy
**Estimated Time**: 10 minutes
**Current Version**: Functional Project #1 with Supabase support

---

## Why Supabase for HAMMER-API?

### Current Problem (SQLite)
- ❌ Local file (`imei_orders.db`) - not shared across Railway replicas
- ❌ Data lost if Railway restarts/redeploys
- ❌ No backups
- ❌ Single point of failure

### Solution (Supabase)
- ✅ Cloud PostgreSQL - accessible from anywhere
- ✅ Automatic daily backups
- ✅ 99.9% uptime SLA
- ✅ Scales to millions of orders
- ✅ Free tier: 500MB database (enough for 50K orders)

---

## Step-by-Step Setup (10 Minutes)

### 1. Create Supabase Project (3 minutes)

1. Go to https://app.supabase.com
2. Sign up (use GitHub for quick signup)
3. Click **"New Project"**
4. Configure project:
   ```
   Name: hammer-api
   Database Password: [Generate Strong Password] ← SAVE THIS!
   Region: us-east-1 (or closest to you)
   Pricing Plan: Free
   ```
5. Click **"Create new project"**
6. Wait ~2 minutes for provisioning ☕

### 2. Create Database Tables (2 minutes)

1. In Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Copy ENTIRE contents from `supabase_schema.sql` in this repo
4. Paste into SQL editor
5. Click **"Run"** (or press Ctrl+Enter)
6. You should see: **"Success. No rows returned"**

**Verify**:
- Go to **"Table Editor"** → should see `orders` and `import_history` tables
- Click `orders` → should see column structure (empty for now)

### 3. Get Your Credentials (1 minute)

1. In Supabase dashboard, go to **Settings** (gear icon) → **API**
2. Copy these TWO values:

   **Project URL** (looks like):
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```

   **anon public key** (long JWT token):
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFz...
   ```

**IMPORTANT**: Copy the **anon** key (NOT service_role). The schema already allows backend access.

### 4. Configure Local Environment (2 minutes)

Edit your `.env` file:

```bash
# GSM Fusion API (existing)
GSM_FUSION_API_KEY=your-existing-key
GSM_FUSION_USERNAME=your-username
GSM_FUSION_BASE_URL=http://hammerfusion.com

# Supabase (NEW - paste your credentials)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional
LOG_LEVEL=INFO
```

### 5. Test Connection Locally (2 minutes)

```bash
# Install Supabase if needed
pip install -r requirements.txt

# Test connection
python3 -c "
import os
os.environ['SUPABASE_URL'] = 'your-url-here'
os.environ['SUPABASE_KEY'] = 'your-key-here'
from database_supabase import get_database
db = get_database()
print(f'✅ Connected! Using: {\"Supabase\" if db.use_supabase else \"SQLite\"}')
"
```

**Expected output**: `✅ Connected! Using: Supabase`

---

## Deploying to Railway

### Update Railway Environment Variables

1. Go to https://railway.app
2. Select your IMEI-PROCESSOR project
3. Click **"Variables"** tab
4. Add TWO new variables:

   ```
   SUPABASE_URL = https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

5. Click **"Deploy"** - Railway will restart with Supabase!

### What Happens Next

Railway will:
1. Restart your application (30 seconds)
2. Detect `SUPABASE_URL` in environment
3. Connect to Supabase automatically
4. All new orders stored in cloud database ✅

### Create Storage Bucket for CSV/Excel Files

**IMPORTANT**: The application now uploads CSV/Excel batch files to Supabase Storage for cloud persistence.

1. In Supabase dashboard, go to **Storage** (left sidebar)
2. Click **"New bucket"**
3. Configure bucket:
   ```
   Name: batch-uploads
   Public bucket: Yes (or configure RLS policies for private access)
   ```
4. Click **"Create bucket"**

**Why This Matters:**
- Uploaded CSV/Excel files are now stored in the cloud
- Files persist across Railway restarts
- Accessible from Supabase dashboard
- Full history of uploaded batch files

**Verify:**
- Upload a test CSV via web interface
- Go to Supabase → Storage → batch-uploads
- Your uploaded file should appear with timestamp prefix

---

## Migrating Existing Data (Optional)

If you have existing orders in SQLite:

### Option 1: Fresh Start (Recommended for Testing)
Just start using Supabase - old SQLite orders stay local, new orders go to Supabase.

### Option 2: Migrate Existing Orders

```bash
# Make sure Supabase env vars are set
export SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
export SUPABASE_KEY=eyJhbGciOi...

# Run migration script
python3 migrate_to_supabase.py
```

The script will:
1. Test Supabase connection
2. Count existing SQLite orders
3. Ask for confirmation
4. Copy all orders to Supabase
5. Show summary

---

## Verification Checklist

After setup, verify everything works:

### 1. Check Supabase Dashboard
- Go to **Table Editor** → **orders**
- Should see table structure (may be empty)

### 2. Test Web Interface Locally
```bash
python3 web_app.py
```
- Visit http://localhost:5001
- Submit a test IMEI order
- Check **Order History** - should show order
- Go back to Supabase → **Table Editor** → **orders** → **Refresh**
- Your test order should appear! ✅

### 3. Test on Railway (After Deployment)
- Visit your Railway URL
- Submit a test IMEI
- Check Supabase Table Editor - should see it!

---

## How It Works (Technical)

### Automatic Database Detection

The new `database_supabase.py` automatically detects which database to use:

```python
# If SUPABASE_URL is set → Use Supabase (PostgreSQL)
# If SUPABASE_URL not set → Use SQLite (local file)
```

### Code Changes Required

**NONE!** The database API is identical:

```python
from database_supabase import get_database

db = get_database()  # Auto-detects Supabase or SQLite
db.insert_order({...})  # Works with both
orders = db.get_recent_orders(100)  # Works with both
```

### Deployment Strategy

**Option A: Replace database.py (Clean)**
```bash
# Backup original
mv database.py database.py.sqlite_backup

# Use Supabase version
mv database_supabase.py database.py

# Commit and deploy
git add database.py
git commit -m "Switch to Supabase for production database"
git push
```

**Option B: Keep Both (Safe)**
- Keep `database.py` (SQLite version)
- Use `database_supabase.py` (new version)
- Update imports in `web_app.py` manually

---

## Switching Back to Working Baseline

If anything goes wrong:

```bash
# Revert to commit 3a7f0e9 (working SQLite version)
git checkout 3a7f0e9
git checkout -b emergency-restore
git push -f origin emergency-restore:main
```

This restores the working SQLite version instantly.

---

## Cost & Scaling

### Free Tier (Current)
- **Database**: 500 MB
- **Capacity**: ~50,000 orders
- **Daily volume**: 5,000-10,000 orders for testing
- **Cost**: $0/month

### Pro Tier ($25/month)
- **Database**: 8 GB
- **Capacity**: ~800,000 orders
- **Daily volume**: 20,000-50,000 orders
- **Backups**: Daily automatic backups
- **Cost**: $25/month

### When to Upgrade
- Approaching 40K orders (80% of free tier)
- Need daily backups
- Processing >5,000 orders/day regularly

---

## Troubleshooting

### Error: "Missing Supabase credentials"
**Fix**: Make sure environment variables are set:
```bash
echo $SUPABASE_URL  # Should show your URL
echo $SUPABASE_KEY  # Should show your key
```

### Error: "relation 'orders' does not exist"
**Fix**: Run `supabase_schema.sql` in Supabase SQL Editor

### Still using SQLite after setting Supabase vars
**Fix**: Restart the application:
```bash
# Kill existing process
pkill -f web_app

# Start fresh
python3 web_app.py
```

### Orders not appearing in Supabase
**Fix**: Check logs:
```bash
tail -f web_app.log | grep -i "supabase\|database"
```

Look for: `✓ Connected to Supabase`

---

## Monitoring (Supabase Dashboard)

### Check Database Size
SQL Editor → Run:
```sql
SELECT pg_size_pretty(pg_database_size(current_database()));
```

### Orders by Status
```sql
SELECT status, COUNT(*) as count, SUM(credits) as total_credits
FROM orders
GROUP BY status
ORDER BY count DESC;
```

### Recent Orders
```sql
SELECT order_id, imei, status, carrier, model, order_date
FROM orders
ORDER BY order_date DESC
LIMIT 10;
```

### Total Credits Spent
```sql
SELECT SUM(credits) as total_credits FROM orders;
```

---

## Summary

**What You Get:**
- ✅ Cloud PostgreSQL database
- ✅ 99.9% uptime
- ✅ Automatic backups (Pro plan)
- ✅ Scales to millions of orders
- ✅ Works seamlessly with existing code
- ✅ Free tier for testing

**Setup Time:** 10 minutes
**Code Changes:** Minimal (just switch import or rename file)
**Rollback Time:** 2 minutes (revert to commit 3a7f0e9)

---

## Next Steps

1. **Complete Steps 1-5 above** (10 minutes)
2. **Test locally** (submit a test order)
3. **Deploy to Railway** (add env vars, redeploy)
4. **Verify in Supabase** (check Table Editor)
5. **Monitor** (watch database size, set alerts)

**Need Help?**
- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- HAMMER-API Docs: See `TECHNICAL_DOCUMENTATION.md`

---

**Ready to go live with enterprise-grade database!** 🚀
