# Railway Deployment Checklist

## Status: Code Pushed, Variables Needed

---

## ✅ Completed Steps

1. ✅ Supabase database created and configured
2. ✅ Code committed to git
3. ✅ Code pushed to GitHub (commit: 1e93a9e)
4. ✅ Railway deployment triggered

---

## ⚠️ Action Required: Add Supabase Variables

### Quick Steps (2 minutes):

**1. Open Railway Dashboard**
```
https://railway.app/dashboard
```

**2. Select Project**
- Click: **IMEI-PROCESSOR**

**3. Add Variables**
- Click: **"Variables"** tab
- Click: **"+ New Variable"**

**Variable 1:**
```
Name:  SUPABASE_URL
Value: https://opinemzfwtoduewqhqwp.supabase.co
```

**Variable 2:**
```
Name:  SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI
```

**4. Save**
- Railway will automatically redeploy (~2 minutes)

**5. Get Live URL**
- In Railway dashboard → **Deployments**
- Copy your live URL (e.g., `https://imei-processor-production.up.railway.app`)
- Visit it!

---

## After Deployment

### Test Your Live System

1. **Visit your Railway URL**
   - You should see the HAMMER-API interface

2. **Submit a test IMEI order**
   - Use any valid IMEI (or test IMEI: `356825821305851`)
   - Select a service
   - Submit

3. **Check Supabase Dashboard**
   - https://supabase.com/dashboard
   - Select project: **opinemzfwtoduewqhqwp**
   - Go to: **Table Editor** → **orders**
   - You should see your order with status "Pending"

4. **Wait for Auto-Sync (5 minutes)**
   - System automatically checks order status
   - When complete, status changes to "Completed"
   - Results populated: carrier, model, simlock, etc.

---

## What You'll Have After Deployment

✅ **Live Web Application**
- Public URL for IMEI submissions
- Web interface for viewing orders

✅ **Cloud Database (Supabase)**
- All orders stored in PostgreSQL
- Searchable by IMEI
- Complete order history

✅ **Auto-Sync**
- Checks pending orders every 5 minutes
- Updates with results automatically

✅ **Scalable**
- Handles 6,000-20,000 orders/day
- Cloud infrastructure

---

## Quick Links

| Service | URL | Purpose |
|---------|-----|---------|
| **Railway Dashboard** | https://railway.app/dashboard | View deployments, logs, settings |
| **Supabase Dashboard** | https://supabase.com/dashboard | View database data |
| **Your Live Site** | (Get from Railway after deploy) | Test orders |

---

## Troubleshooting

### If deployment fails:

1. **Check Railway logs:**
   - Railway Dashboard → Deployments → View Logs

2. **Verify variables are set:**
   - Railway Dashboard → Variables
   - Should see `SUPABASE_URL` and `SUPABASE_KEY`

3. **Check Supabase connection:**
   - Logs should show: `✓ Connected to Supabase`
   - If not, verify variables are correct

### If Supabase not connecting:

1. **Verify credentials:**
   ```bash
   # Test locally
   python3 -c "
   import os
   os.environ['SUPABASE_URL']='https://opinemzfwtoduewqhqwp.supabase.co'
   os.environ['SUPABASE_KEY']='eyJhbG...'
   from database_supabase import get_database
   db = get_database()
   print('Connected!' if db.use_supabase else 'Failed')
   "
   ```

2. **Check Supabase project status:**
   - Make sure project is active
   - Verify tables exist (run schema SQL again if needed)

---

## Rollback (If Needed)

If something goes wrong:

```bash
# Revert to previous version
git checkout d810d12
git push -f origin working-version-restore

# Or use Railway dashboard:
# Deployments → Find working deployment → Redeploy
```

---

## Documentation

- **Full Data Flow:** `SUPABASE_DATA_FLOW.md`
- **Deployment Script:** `DEPLOY_TO_RAILWAY.sh`
- **Parser Guide:** `PARSER_GUIDE.md`

---

**Created:** 2025-11-18
**Status:** Ready to add Railway variables
**Next:** Add Supabase variables in Railway Dashboard

🚀 **Your system is ready to go live!**
