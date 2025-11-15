# CSV Export to Supabase Storage - Setup Guide

**Status**: Ready to Deploy
**Estimated Time**: 5 minutes
**Feature**: Export completed IMEI orders to CSV and store in cloud

---

## What This Does

When you click "Export Completed Orders" in the web interface:
1. Queries database for all orders with status = 'Completed'
2. Generates CSV file with all order details (IMEI, carrier, model, status, etc.)
3. Uploads CSV to Supabase Storage (cloud file storage)
4. Returns public URL for download/sharing

**This is NOT saving uploaded CSV files - it's generating CSV exports of completed orders from the database.**

---

## Prerequisites

You've already completed most of the setup! Your credentials are:
- **Supabase URL**: https://opinemzfwtoduewqhqwp.supabase.co
- **Supabase Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (stored in .env)

---

## Step 1: Create Storage Bucket (2 minutes)

1. Go to https://app.supabase.com
2. Select your project: **opinemzfwtoduewqhqwp**
3. Click **Storage** in left sidebar
4. Click **"New bucket"**
5. Configure bucket:
   ```
   Name: batch-uploads
   Public bucket: Yes (if you want URLs to be accessible)
   File size limit: 50 MB (default is fine)
   Allowed MIME types: Leave empty (allow all)
   ```
6. Click **"Create bucket"**

**Verify**: You should see "batch-uploads" in your bucket list.

---

## Step 2: Configure Environment Variables (1 minute)

### Local Development

Your `.env` file should already have:
```bash
# Supabase (for database + storage)
SUPABASE_URL=https://opinemzfwtoduewqhqwp.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI
```

### Railway Deployment

1. Go to https://railway.app
2. Select your **HAMMER-API** project
3. Click **"Variables"** tab
4. Verify these variables exist (add if missing):
   ```
   SUPABASE_URL = https://opinemzfwtoduewqhqwp.supabase.co
   SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI
   ```
5. Click **"Deploy"** if you made changes

---

## Step 3: Test Locally (2 minutes)

### Option A: Test via Web Interface

```bash
# Start web server
python3 web_app.py
```

1. Visit http://localhost:5001/database
2. You should see two new buttons:
   - **"Export to Cloud CSV"** (green) - Exports completed orders
   - **"Export All to Cloud CSV"** - Exports all orders
3. Click **"Export to Cloud CSV"**
4. You should see a success message with the CSV URL

### Option B: Test via Command Line

```bash
# Export completed orders
python3 export_completed_orders.py

# Or export with specific status
python3 export_completed_orders.py "In Process"
```

**Expected output**:
```
============================================================
Export Completed Orders to CSV
============================================================

Exporting orders with status: Completed (default)

============================================================
✅ Export successful!
CSV URL: https://opinemzfwtoduewqhqwp.supabase.co/storage/v1/object/public/batch-uploads/completed_orders_20251115_143020.csv

You can:
1. Download: curl -o export.csv 'https://...'
2. Share the URL with your team
3. Import to Excel, Google Sheets, etc.
============================================================
```

---

## Step 4: Verify in Supabase Dashboard

1. Go to https://app.supabase.com
2. Select your project
3. Click **Storage** → **batch-uploads**
4. You should see your exported CSV file(s)
5. Click file name to download or get public URL

---

## Usage Guide

### Web Interface

**Location**: `/database` page

**Buttons**:
1. **Export to Cloud CSV** (green button)
   - Exports all orders with status = 'Completed'
   - Returns public URL for download
   - Redirects back to database page with success message

2. **Export All to Cloud CSV**
   - Exports all recent orders (any status)
   - Default limit: 10,000 orders
   - Returns public URL for download

**What Happens**:
- CSV is generated in memory
- Uploaded to Supabase Storage
- Public URL is returned
- Flash message shows URL for download

### Command Line

```bash
# Export completed orders
python3 export_completed_orders.py

# Export orders with specific status
python3 export_completed_orders.py "Pending"
python3 export_completed_orders.py "In Process"

# Export all orders (programmatically)
python3 -c "
from export_completed_orders import export_all_orders_to_csv
url = export_all_orders_to_csv(limit=5000)
print(f'Exported to: {url}')
"
```

### API Integration (Advanced)

```python
from export_completed_orders import export_completed_orders_to_csv

# Export completed orders
csv_url = export_completed_orders_to_csv()
if csv_url:
    print(f"CSV exported: {csv_url}")
    # Send URL via email, Slack, etc.
```

---

## CSV Format

**Columns Included**:
- `order_id` - GSM Fusion order ID
- `imei` - Primary IMEI (15 digits)
- `imei2` - Secondary IMEI (dual-SIM devices)
- `service_name` - Service display name
- `service_id` - Service package ID
- `status` - Completed, Pending, In Process, Rejected
- `carrier` - Carrier name (e.g., T-Mobile, AT&T)
- `model` - Device model (e.g., iPhone 12 Pro)
- `simlock` - Lock status (e.g., Unlocked, Locked to T-Mobile)
- `fmi` - Find My iPhone status (On/Off)
- `credits` - Cost in credits
- `order_date` - When order was placed
- `result_code` - Raw result code from API
- `result_code_display` - Cleaned result code (HTML removed)
- `notes` - Additional notes
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp

**Example CSV**:
```csv
order_id,imei,status,carrier,model,simlock,fmi,credits,order_date
12345678,123456789012345,Completed,T-Mobile,iPhone 12 Pro,Unlocked,Off,1.50,2025-11-15 14:30:00
12345679,123456789012346,Completed,AT&T,iPhone 13,Locked to AT&T,On,1.50,2025-11-15 14:31:00
```

---

## Automatic Export (Optional)

To automatically export completed orders after batch processing:

### Option 1: Export After Batch Upload

Edit `web_app.py` batch route (around line 800):

```python
# After batch processing completes
flash(f'Batch processed: {successful} successful...', 'success')

# Auto-export completed orders
from export_completed_orders import export_completed_orders_to_csv
csv_url = export_completed_orders_to_csv()
if csv_url:
    flash(f'✅ Exported to: {csv_url}', 'info')

return redirect(url_for('history'))
```

### Option 2: Scheduled Export (Cron Job)

```bash
# Add to crontab (export every hour)
0 * * * * cd /path/to/HAMMER-API && python3 export_completed_orders.py >> export.log 2>&1

# Export daily at 11 PM
0 23 * * * cd /path/to/HAMMER-API && python3 export_completed_orders.py >> export.log 2>&1
```

---

## Troubleshooting

### Error: "Supabase Storage not available"

**Cause**: Environment variables not set

**Fix**:
```bash
# Check if set
echo $SUPABASE_URL
echo $SUPABASE_KEY

# If empty, load .env
export $(cat .env | xargs)

# Or set manually
export SUPABASE_URL=https://opinemzfwtoduewqhqwp.supabase.co
export SUPABASE_KEY=eyJhbGciOi...
```

### Error: "The resource was not found"

**Cause**: Storage bucket doesn't exist

**Fix**: Create 'batch-uploads' bucket in Supabase dashboard (see Step 1)

### Error: "No orders found with status 'Completed'"

**Cause**: No completed orders in database yet

**Fix**:
- Submit test orders via web interface
- Wait for orders to complete (status changes from Pending → Completed)
- Or test with different status: `python3 export_completed_orders.py "Pending"`

### Error: "Permission denied" when uploading

**Cause**: Bucket is private or RLS policies are blocking

**Fix**:
1. Go to Supabase dashboard → Storage → batch-uploads
2. Click **"Policies"**
3. Add policy: "Allow insert for service role"
4. Or make bucket public in settings

### Export button not showing

**Cause**: Template not updated or cached

**Fix**:
```bash
# Clear browser cache (Cmd+Shift+R on Mac)
# Or restart web server
pkill -f web_app
python3 web_app.py
```

---

## File Management

### List All Exported Files

```python
from export_completed_orders import list_exported_csvs

files = list_exported_csvs(limit=50)
for file in files:
    print(f"{file['name']} - {file['size']} bytes - {file['created_at']}")
```

### Delete Old Files

```python
from supabase_storage import get_storage

storage = get_storage()
deleted_count = storage.delete_old_files(days=30)  # Delete files older than 30 days
print(f"Deleted {deleted_count} old files")
```

### Download Exported CSV

```bash
# Get CSV URL from web interface or logs
CSV_URL="https://opinemzfwtoduewqhqwp.supabase.co/storage/v1/object/public/batch-uploads/completed_orders_20251115_143020.csv"

# Download
curl -o export.csv "$CSV_URL"

# Or use wget
wget -O export.csv "$CSV_URL"
```

---

## Security Considerations

### Public vs Private Buckets

**Public Bucket** (Current Setup):
- ✅ Easy to share URLs
- ✅ Direct downloads without auth
- ⚠️ Anyone with URL can access
- **Use if**: Sharing with team, no sensitive data

**Private Bucket**:
- ✅ Requires authentication to access
- ✅ Better for sensitive customer data
- ❌ More complex to share URLs
- **Use if**: IMEI data is confidential

### Changing to Private Bucket

1. Supabase dashboard → Storage → batch-uploads
2. Settings → **Make bucket private**
3. Generate signed URLs for downloads:

```python
from supabase_storage import get_storage

storage = get_storage()
signed_url = storage.client.storage.from_('batch-uploads').create_signed_url(
    'completed_orders_20251115_143020.csv',
    expires_in=3600  # 1 hour expiration
)
```

---

## Cost & Storage Limits

### Supabase Free Tier
- **Storage**: 1 GB free
- **Bandwidth**: 2 GB free per month
- **Typical CSV size**: 1 KB per order (1000 orders ≈ 1 MB)

**Capacity Estimates**:
- 1 GB = ~1,000,000 orders (assuming 1 KB per order)
- Free tier can store 1000+ CSV exports
- Daily exports of 10,000 orders = ~10 MB/day = ~300 MB/month

### When to Upgrade

Upgrade to **Pro Plan ($25/month)** if:
- Approaching 800 MB storage (80% of 1 GB)
- Downloading >1.5 GB/month
- Need automatic backups
- Processing >50,000 orders/day

---

## Integration with Other Systems

### Send CSV to Email

```python
import smtplib
from email.mime.text import MIMEText

csv_url = export_completed_orders_to_csv()
if csv_url:
    msg = MIMEText(f"Completed orders exported: {csv_url}")
    msg['Subject'] = "Daily IMEI Export"
    msg['To'] = "team@example.com"

    # Send email (configure SMTP settings)
    # ...
```

### Push to Google Sheets

```python
import gspread

csv_url = export_completed_orders_to_csv()
if csv_url:
    # Download CSV
    import requests
    response = requests.get(csv_url)
    csv_data = response.text

    # Upload to Google Sheets
    gc = gspread.service_account()
    sh = gc.open("IMEI Orders")
    worksheet = sh.sheet1
    worksheet.clear()
    # Import CSV data...
```

### Webhook Notification

```python
import requests

csv_url = export_completed_orders_to_csv()
if csv_url:
    # Send to Slack, Discord, etc.
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={
        "text": f"📊 New IMEI export available: {csv_url}"
    })
```

---

## Summary

**What You Get**:
- ✅ One-click CSV export from web interface
- ✅ Cloud storage (persistent, not lost on Railway restarts)
- ✅ Public URLs for easy sharing
- ✅ Command-line export for automation
- ✅ 1 GB free storage (1,000,000+ orders)
- ✅ Automatic file management (delete old exports)

**Setup Time**: 5 minutes
**Files Added**:
- `export_completed_orders.py` (new module)
- `supabase_storage.py` (already exists)
- Updated `web_app.py` (3 new routes)
- Updated `templates/database.html` (2 new buttons)

**Next Steps**:
1. Create 'batch-uploads' bucket in Supabase dashboard
2. Test export via web interface
3. Share CSV URLs with your team
4. Set up automatic exports (optional)

---

**Ready to export completed IMEI orders to the cloud!** 🚀
