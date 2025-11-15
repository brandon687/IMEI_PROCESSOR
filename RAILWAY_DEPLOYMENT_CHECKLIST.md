# Railway Deployment Checklist

## ✅ Code Pushed to GitHub

**Commit**: `42e5166` - "Add Supabase Storage CSV export and fix critical routes"

**Branch**: `working-version-restore` → pushed to `main`

**GitHub URL**: https://github.com/brandon687/IMEI_PROCESSOR

---

## 🔧 Environment Variables to Add in Railway

Go to Railway dashboard → Your project → **Variables** tab

### Required Variables

Make sure these variables exist:

```bash
# GSM Fusion API (existing)
GSM_FUSION_API_KEY=I7E1-K5C7-E8R5-P1V6-A2P8
GSM_FUSION_USERNAME=scalmobile
GSM_FUSION_BASE_URL=https://hammerfusion.com

# Supabase (NEW - add these if missing)
SUPABASE_URL=https://opinemzfwtoduewqhqwp.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI

# Optional
LOG_LEVEL=INFO
ENABLE_PROGRESSIVE_LOADING=true
```

### How to Add Variables

1. Go to https://railway.app
2. Select your **HAMMER-API** project
3. Click **"Variables"** tab (left sidebar)
4. Click **"New Variable"**
5. Add each variable:
   - Name: `SUPABASE_URL`
   - Value: `https://opinemzfwtoduewqhqwp.supabase.co`
6. Repeat for `SUPABASE_KEY`
7. Click **"Deploy"** button (top right)

---

## 📦 What Was Deployed

### New Features

1. **CSV Export to Supabase Storage**
   - Export completed orders: `/export-completed`
   - Export all orders: `/export-all`
   - Buttons on `/database` page

2. **Order Sync Route**
   - Updates pending orders from API: `/history/sync`
   - Button on `/history` page

3. **Supabase Storage Integration**
   - Batch CSV files uploaded to cloud
   - Persistent storage (survives Railway restarts)

### Fixed Issues

1. Export route redirect error (`database` → `database_view`)
2. Missing sync route (404 → working route)
3. Batch upload file storage to Supabase

---

## 🚀 Verify Deployment

### Step 1: Wait for Railway Build

1. Go to Railway dashboard → **Deployments** tab
2. Wait for build to complete (usually 2-3 minutes)
3. Look for: "✅ Build successful"

### Step 2: Check Deployment Logs

Click on latest deployment → **View Logs**

**Look for**:
```
✓ Cache warmed with 236 services
Starting Flask on port 5001
Running on http://0.0.0.0:5001
```

**Should NOT see**:
- "SUPABASE_URL not set" warnings
- Import errors
- Port errors

### Step 3: Test Live Application

Visit your Railway URL (e.g., `https://your-app.up.railway.app`)

**Test these pages**:
1. Homepage: Should load without errors
2. Database page: Should show export buttons
3. History page: Should show sync button
4. Click export button: Should see success message with CSV URL

---

## 🐛 Troubleshooting

### Error: "Supabase Storage not available"

**Cause**: Environment variables not set in Railway

**Fix**:
1. Go to Railway → Variables
2. Add `SUPABASE_URL` and `SUPABASE_KEY`
3. Redeploy

### Error: "Module not found: supabase"

**Cause**: Missing dependency in requirements.txt

**Fix**: Already fixed in commit (supabase-py added)

### Export button gives 500 error

**Cause**: RLS policies not set in Supabase

**Fix**: Already fixed (policies created in Supabase dashboard)

### Sync button doesn't work

**Cause**: Route missing or redirect error

**Fix**: Already fixed in this commit

---

## 📊 Expected Behavior After Deployment

### Database Page (`/database`)

- Shows 4 action cards:
  1. Import Data
  2. **Export Completed Orders** (green button)
  3. **Export All Orders** (button)
  4. Search

- Clicking export buttons:
  - Redirects back to database page
  - Shows flash message: "✅ Exported X orders to CSV: [URL]"
  - CSV URL is publicly accessible

### History Page (`/history`)

- Shows "🔄 Sync Status" button (top right)
- Clicking sync:
  - Fetches updates from GSM Fusion API
  - Updates pending orders in database
  - Shows: "✅ Synced X orders successfully"

### Supabase Storage

- Check Storage → batch-uploads bucket
- Should see uploaded CSV files:
  - `completed_orders_YYYYMMDD_HHMMSS.csv`
  - `test_export_YYYYMMDD_HHMMSS.csv`

---

## ✅ Deployment Complete Checklist

- [ ] Code pushed to GitHub main branch
- [ ] Railway environment variables added (SUPABASE_URL, SUPABASE_KEY)
- [ ] Railway deployment build successful
- [ ] Application starts without errors in logs
- [ ] Homepage loads correctly
- [ ] Database page shows export buttons
- [ ] History page shows sync button
- [ ] Export button works (generates CSV URL)
- [ ] CSV file visible in Supabase Storage
- [ ] Sync button updates pending orders

---

## 🎉 Success Criteria

**Deployment is successful when**:
1. Railway build completes without errors
2. Application starts and serves requests
3. Export buttons generate CSV URLs
4. CSV files appear in Supabase Storage
5. Sync button updates order statuses

**Test URL**: Visit your Railway app URL and test export/sync features

---

## 📝 Notes

- **Working version baseline**: Commit `3a7f0e9` (documented in WORKING_VERSION_BASELINE.md)
- **Current version**: Commit `42e5166` (with Supabase features)
- **Branch**: `working-version-restore` (merged to main)
- **Railway builder**: NIXPACKS (automatic detection)
- **Python version**: 3.9+ (from runtime.txt or auto-detected)

If anything fails, you can rollback to baseline commit `3a7f0e9`.
