# Fix Supabase Storage RLS - Updated Guide

## Current Supabase Interface (2025)

The RLS settings for Storage buckets are in a different location. Follow these steps:

### Method 1: Make Bucket Public (Easiest)

1. In Supabase dashboard → **Storage** → **batch-uploads**
2. Look for bucket settings (usually top right corner or in the bucket header)
3. Find **"Public bucket"** toggle or checkbox
4. **Enable** "Public bucket" (this automatically allows uploads/downloads)
5. Save changes

**OR**

### Method 2: Add Storage Policies via SQL

Since the UI might not show storage policies clearly, use the SQL Editor:

1. Go to **SQL Editor** in left sidebar (not Storage)
2. Click **"New query"**
3. Paste this SQL:

```sql
-- Allow anyone to upload files to batch-uploads bucket
INSERT INTO storage.policies (name, bucket_id, definition, check_expression)
VALUES (
  'Allow public uploads',
  'batch-uploads',
  '(true)',
  '(true)'
)
ON CONFLICT DO NOTHING;

-- Allow anyone to read files from batch-uploads bucket
INSERT INTO storage.policies (name, bucket_id, definition, check_expression)
VALUES (
  'Allow public downloads',
  'batch-uploads',
  '(true)',
  '(true)'
)
ON CONFLICT DO NOTHING;
```

4. Click **"Run"**
5. Should see: "Success. No rows returned"

### Method 3: Use Supabase CLI (Advanced)

If you have Supabase CLI installed:

```bash
# Disable RLS for storage.objects table
supabase db execute "ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;"
```

---

## Quick Test After Fix

Run this to verify it works:

```bash
export SUPABASE_URL='https://opinemzfwtoduewqhqwp.supabase.co' && \
export SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI' && \
python3 -c "
import os, csv, io
from datetime import datetime
from supabase import create_client

supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

csv_buffer = io.StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=['order_id', 'imei', 'status'])
writer.writeheader()
writer.writerow({'order_id': 'TEST001', 'imei': '123456789012345', 'status': 'Completed'})

csv_bytes = csv_buffer.getvalue().encode('utf-8')
filename = f'test_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.csv'

result = supabase.storage.from_('batch-uploads').upload(filename, csv_bytes, {'content-type': 'text/csv'})
url = supabase.storage.from_('batch-uploads').get_public_url(filename)

print('✅ SUCCESS! Upload works!')
print(f'URL: {url}')
"
```

---

## Alternative: Check Bucket Configuration

In your screenshot, look for:
- **Configuration** tab (might be next to "Objects")
- **Settings** icon/button near the bucket name
- **Public Access** toggle or setting
- **Policies** link in the bucket view

The key is to either:
1. Make bucket public, OR
2. Add permissive RLS policies via SQL Editor

Try Method 2 (SQL Editor) - it's the most reliable approach.
