# Supabase Storage Fix - Correct SQL

## The Issue
The `storage.policies` table doesn't exist in newer Supabase versions. Storage uses standard RLS policies on the `storage.objects` table.

## Correct SQL (Copy and Paste)

Go to **SQL Editor** in Supabase and run this:

```sql
-- Create policy to allow public uploads to batch-uploads bucket
CREATE POLICY "Allow public uploads to batch-uploads"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'batch-uploads');

-- Create policy to allow public downloads from batch-uploads bucket
CREATE POLICY "Allow public downloads from batch-uploads"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'batch-uploads');

-- Create policy to allow public updates (optional, for overwriting files)
CREATE POLICY "Allow public updates to batch-uploads"
ON storage.objects
FOR UPDATE
TO public
USING (bucket_id = 'batch-uploads')
WITH CHECK (bucket_id = 'batch-uploads');
```

## Expected Result

You should see:
```
Success. No rows returned
```

Or a success message for each policy created.

## Alternative: Simpler Approach

If you want to disable RLS completely for storage (easier for testing):

```sql
-- Disable RLS on storage.objects table
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
```

**WARNING**: This disables RLS for ALL storage buckets, not just batch-uploads. Use the first approach for better security.

---

## Test After Running SQL

Once you run either SQL option, test immediately:

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

print(f'Uploading test file: {filename}')
result = supabase.storage.from_('batch-uploads').upload(filename, csv_bytes, {'content-type': 'text/csv'})
url = supabase.storage.from_('batch-uploads').get_public_url(filename)

print('✅ SUCCESS! Upload works!')
print(f'URL: {url}')
print(f'\\nTest download: curl {url}')
"
```

---

## Summary

**Use this SQL** (in SQL Editor):

```sql
CREATE POLICY "Allow public uploads to batch-uploads"
ON storage.objects FOR INSERT TO public
WITH CHECK (bucket_id = 'batch-uploads');

CREATE POLICY "Allow public downloads from batch-uploads"
ON storage.objects FOR SELECT TO public
USING (bucket_id = 'batch-uploads');
```

Then test with the command above.
