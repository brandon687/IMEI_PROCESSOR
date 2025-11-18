# CSV Format Updated to Match GSM Fusion

## Changes Made

The CSV export now uses the **exact GSM Fusion format**:

### Format Details

**Delimiter**: Tab-separated (TSV, not comma CSV)

**Headers** (exact order):
```
SERVICE	IMEI NO.	CREDITS	STATUS	CODE	IMEI 2	CARRIER	SIMLOCK	MODEL	FMI	ORDER DATE	NOTES
```

**Example Row**:
```
10-7.1# Apple iPhone IMEI Carrier + Simlock + FMI + WW + Activation Etc 🔥Hot Exclusive Checker🔥	664875798745687	$0.08	In Process							2025-11-15 22:27:34	
```

### Key Features

1. **Tab-separated** - Use `\t` delimiter (not commas)
2. **Credits with $** - Formatted as `$0.08` (not `0.08`)
3. **Exact column names** - Uppercase, with spaces and periods
4. **Empty fields** - Show as tabs with no content (not "N/A")

---

## Field Mapping

| GSM Fusion Column | Database Field | Notes |
|-------------------|----------------|-------|
| SERVICE | service_name | Full service name |
| IMEI NO. | imei | 15-digit IMEI |
| CREDITS | credits | Formatted with $ prefix |
| STATUS | status | Completed, Pending, In Process, etc. |
| CODE | result_code_display | Cleaned result code (HTML stripped) |
| IMEI 2 | imei2 | Second IMEI for dual-SIM |
| CARRIER | carrier | T-Mobile, AT&T, etc. |
| SIMLOCK | simlock | Unlocked, Locked to Carrier |
| MODEL | model | iPhone 12 Pro, etc. |
| FMI | fmi | Find My iPhone status |
| ORDER DATE | order_date | YYYY-MM-DD HH:MM:SS |
| NOTES | notes | Additional notes |

---

## Updated Functions

### export_completed_orders.py
- `export_completed_orders_to_csv()` - Cloud export (completed)
- `export_all_orders_to_csv()` - Cloud export (all orders)

### web_app.py
- `/download-csv` - Direct download (all orders)
- `/download-completed-csv` - Direct download (completed)

All four export functions now use the same GSM Fusion format.

---

## Testing

### Test Direct Download
1. Visit http://localhost:5001/database
2. Click "📥 Completed Orders" under Download CSV
3. Open downloaded file in Excel/Sheets
4. Verify format matches GSM Fusion exactly

### Test Cloud Export
1. Visit http://localhost:5001/database
2. Click "☁️ Completed Orders" under Cloud Export
3. Copy returned URL and open in browser
4. Verify format matches GSM Fusion exactly

### Expected Format
```
SERVICE	IMEI NO.	CREDITS	STATUS	CODE	IMEI 2	CARRIER	SIMLOCK	MODEL	FMI	ORDER DATE	NOTES
Service Name Here	123456789012345	$1.50	Completed	Result Code	123456789012346	T-Mobile	Unlocked	iPhone 12	Off	2025-11-15 14:30:00	Notes here
```

---

## Import Compatibility

This format is now **100% compatible** with GSM Fusion exports, meaning you can:

1. **Export from HAMMER-API** → Import to spreadsheet
2. **Export from GSM Fusion** → Compare side-by-side
3. **Merge files** - Same format, easy to combine
4. **Re-import** - Can reimport your exports if needed

---

## Technical Details

### Code Changes

**Before** (comma CSV with different headers):
```python
fieldnames = ['order_id', 'imei', 'status', 'carrier', ...]
writer = csv.DictWriter(output, fieldnames=fieldnames)  # comma delimiter
```

**After** (tab-separated with GSM Fusion headers):
```python
fieldnames = ['SERVICE', 'IMEI NO.', 'CREDITS', 'STATUS', ...]
writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter='\t')  # tab delimiter
```

**Credits Formatting**:
```python
credits = order.get('credits', '')
if credits and str(credits).replace('.', '', 1).isdigit():
    credits = f"${credits}"  # Add $ prefix
```

---

## File Extension

Files are still saved as `.csv` but contain tab-separated values. This is standard for TSV files exported as CSV.

**Filename format**:
- Direct download: `completed_orders_20251115_142530.csv`
- Cloud export: `completed_orders_20251115_142530.csv`

Excel and Google Sheets automatically detect tab-separated format.

---

## Deployment Status

**Local**: ✅ Working - http://localhost:5001

**GitHub**: ✅ Pushed - Commit `641120c`

**Railway**: 🔄 Auto-deploying (2-3 minutes)

**Supabase**: ✅ Ready - Storage bucket configured

---

## Summary

All CSV exports now match the **exact GSM Fusion format**:
- Tab-separated values (TSV)
- Correct column headers and order
- $ prefix on credits
- Compatible with GSM Fusion exports

Both download and cloud export methods use this format!
