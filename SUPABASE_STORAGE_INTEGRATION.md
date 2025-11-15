# Supabase Storage Integration - Quick Fix

## Issue Detected

Your bucket `batch-uploads` has **Row Level Security (RLS)** enabled, which is blocking file uploads.

**Error**: `new row violates row-level security policy`

---

## Quick Fix (2 minutes)

### Option 1: Disable RLS (Easiest - Recommended for Testing)

1. Go to https://app.supabase.com
2. Select project: **opinemzfwtoduewqhqwp**
3. Click **Storage** in left sidebar
4. Click on **batch-uploads** bucket
5. Click the **Settings** (gear icon) or **Policies** tab
6. Find the **"Enable RLS"** toggle
7. **Turn OFF** RLS for this bucket

**Done!** Test again immediately after.

---

### Option 2: Add RLS Policy (More Secure)

If you want to keep RLS enabled for security:

1. Go to https://app.supabase.com
2. Select project → **Storage** → **batch-uploads**
3. Click **Policies** tab
4. Click **"New Policy"**
5. Choose **"For full customization"**
6. Configure policy:
   ```
   Policy name: Allow all uploads
   Allowed operation: INSERT
   Target roles: anon, authenticated
   USING expression: true
   WITH CHECK expression: true
   ```
7. Click **"Review"** → **"Save Policy"**

Also add a SELECT policy for downloads:
1. Click **"New Policy"** again
2. Configure:
   ```
   Policy name: Allow all downloads
   Allowed operation: SELECT
   Target roles: anon, authenticated
   USING expression: true
   ```
3. Click **"Review"** → **"Save Policy"**

---

## Test After Fix

Run this command to verify:

```bash
python3 export_completed_orders.py
```

**Expected output**:
```
✅ Export successful!
CSV URL: https://opinemzfwtoduewqhqwp.supabase.co/storage/v1/object/public/batch-uploads/completed_orders_20251115_140500.csv
```

---

## Summary

**Current Status**: Bucket exists ✅, Credentials set ✅, RLS blocking uploads ❌

**Fix Needed**: Disable RLS or add upload/download policies (2 minutes in Supabase dashboard)

**Next Step**: Fix RLS → Test export → Success!
