# Production Error Fix - Comprehensive Implementation Plan

## Executive Summary

**Production Issues Identified:**
1. `IMEIOrder` dataclass missing 6 attributes causing AttributeError in web_app.py:945-950
2. `history.html` template expects undefined variable `search_count` (line 45)

**Root Cause:**
The GSM Fusion API returns order details in a nested HTML structure within the `code` field, NOT as separate top-level attributes. The current `IMEIOrder` dataclass only has 6 fields (id, imei, package, status, code, requested_at) but web_app.py tries to access 6 additional fields that don't exist.

**Impact:**
- Order sync fails silently for order 15580047 (failed 3 retries)
- History page crashes when searching multiple IMEIs
- Database updates incomplete

---

## Problem Analysis

### Error #1: Missing IMEIOrder Attributes

**Location:** gsm_fusion_client.py:41-48

**Current IMEIOrder dataclass:**
```python
@dataclass
class IMEIOrder:
    """Represents an IMEI order"""
    id: str
    imei: str
    package: str
    status: str
    code: Optional[str] = None
    requested_at: Optional[str] = None
```

**Where it breaks:** web_app.py:944-951 (sync_orders function)
```python
cursor.execute("""
    UPDATE orders
    SET status = ?,
        carrier = ?,        # ❌ AttributeError: 'IMEIOrder' object has no attribute 'carrier'
        model = ?,          # ❌ AttributeError: 'IMEIOrder' object has no attribute 'model'
        simlock = ?,        # ❌ AttributeError: 'IMEIOrder' object has no attribute 'simlock'
        fmi = ?,            # ❌ AttributeError: 'IMEIOrder' object has no attribute 'fmi'
        result_code = ?,    # ❌ AttributeError: 'IMEIOrder' object has no attribute 'result_code'
        result_code_display = ?,  # ❌ AttributeError: 'IMEIOrder' object has no attribute 'result_code_display'
        updated_at = CURRENT_TIMESTAMP
    WHERE order_id = ?
""", (
    order.status,
    order.carrier or '',       # ❌ CRASH HERE
    order.model or '',
    order.simlock or '',
    order.fmi or '',
    order.result_code or '',
    order.result_code_display or '',
    order.id
))
```

**API Response Reality:**
The API returns these fields EMBEDDED in the `code` field as HTML:
```xml
<code>
    Carrier: T-Mobile<br>
    SimLock: Unlocked<br>
    Model: iPhone 12 Pro<br>
    Find My iPhone: OFF<br>
    IMEI2 Number: 355804085587571<br>
</code>
```

**Evidence:** manual_sync.py:45-87 shows the correct parsing logic

---

### Error #2: Template Variable Missing

**Location:** templates/history.html:45

**Current template code:**
```html
{% if search_query %}
    {% if search_count > 1 %}  <!-- ❌ search_count is undefined -->
        Showing {{ orders|length }} order(s) for <strong>{{ search_count }} IMEIs</strong> searched
    {% else %}
```

**Where it's passed:** web_app.py:883-885 (history function)
```python
return render_template('history.html',
                     orders=orders,
                     search_query=search_imei)  # ❌ search_count NOT passed
```

---

## Database Schema Compatibility Check

**Current database schema** (database.py:39-60):
```sql
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    service_name TEXT,
    service_id TEXT,
    imei TEXT NOT NULL,
    imei2 TEXT,
    credits REAL,
    status TEXT,
    carrier TEXT,           ✅ EXISTS
    simlock TEXT,           ✅ EXISTS
    model TEXT,             ✅ EXISTS
    fmi TEXT,               ✅ EXISTS
    order_date TIMESTAMP,
    result_code TEXT,       ✅ EXISTS
    result_code_display TEXT, ✅ EXISTS (with migration at line 63-69)
    notes TEXT,
    raw_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**✅ Database schema is compatible** - all columns exist.

---

## Solution Design

### Option A: Add Fields to IMEIOrder (Recommended)

**Pros:**
- Matches expected interface
- No breaking changes to web_app.py
- Clean separation of concerns

**Cons:**
- Must parse HTML in get_imei_orders()
- Slightly more complex client code

### Option B: Change web_app.py to Parse code Field

**Pros:**
- IMEIOrder stays minimal
- Parsing logic in one place (web_app.py)

**Cons:**
- Breaks existing code patterns (manual_sync.py already parses)
- Duplicates parsing logic
- Less reusable

**Decision:** **Option A** - Add fields to IMEIOrder and parse in client

---

## Implementation Plan

### Phase 1: Update IMEIOrder Dataclass

**File:** gsm_fusion_client.py

**Changes Required:**

1. **Add new fields to IMEIOrder** (line 41-48)
```python
@dataclass
class IMEIOrder:
    """Represents an IMEI order"""
    id: str
    imei: str
    package: str
    status: str
    code: Optional[str] = None
    requested_at: Optional[str] = None
    # NEW FIELDS (parsed from code field):
    carrier: Optional[str] = None
    model: Optional[str] = None
    simlock: Optional[str] = None
    fmi: Optional[str] = None
    imei2: Optional[str] = None
    result_code: Optional[str] = None
    result_code_display: Optional[str] = None
```

2. **Add HTML parsing helper method** (after _xml_to_dict, ~line 283)
```python
def _parse_code_field(self, code: str) -> Dict[str, str]:
    """
    Parse HTML-formatted code field into individual attributes
    
    Args:
        code: HTML string like "Carrier: T-Mobile<br>SimLock: Unlocked<br>..."
    
    Returns:
        Dictionary with parsed fields: carrier, model, simlock, fmi, imei2,
        result_code (original), result_code_display (cleaned)
    """
    import re
    
    if not code:
        return {}
    
    result = {}
    
    # Helper: Clean HTML tags
    def clean_html(text):
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text.strip()
    
    # Clean full code for display
    cleaned_code = code.replace('<br>', '\n').replace('&lt;br&gt;', '\n')
    cleaned_code = clean_html(cleaned_code)
    cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)  # Remove blank lines
    result['result_code_display'] = cleaned_code.strip()
    
    # Keep original code
    result['result_code'] = code
    
    # Extract individual fields
    if 'Carrier:' in code:
        carrier = code.split('Carrier:')[1].split('<br>')[0]
        result['carrier'] = clean_html(carrier)
    
    if 'SimLock:' in code or 'SIM Lock:' in code:
        simlock_key = 'SimLock:' if 'SimLock:' in code else 'SIM Lock:'
        simlock = code.split(simlock_key)[1].split('<br>')[0]
        result['simlock'] = clean_html(simlock)
    
    if 'Model:' in code:
        model = code.split('Model:')[1].split('<br>')[0]
        result['model'] = clean_html(model)
    
    if 'Find My iPhone:' in code or 'FMI:' in code:
        fmi_key = 'Find My iPhone:' if 'Find My iPhone:' in code else 'FMI:'
        fmi = code.split(fmi_key)[1].split('<br>')[0]
        result['fmi'] = clean_html(fmi)
    
    if 'IMEI2 Number:' in code or 'IMEI 2:' in code:
        imei2_key = 'IMEI2 Number:' if 'IMEI2 Number:' in code else 'IMEI 2:'
        imei2 = code.split(imei2_key)[1].split('<br>')[0]
        result['imei2'] = clean_html(imei2)
    
    return result
```

3. **Update get_imei_orders to parse code field** (line 548-557)
```python
for imei_data in imeis_data:
    # Parse code field if present
    parsed_fields = {}
    if imei_data.get('code'):
        parsed_fields = self._parse_code_field(imei_data.get('code'))
    
    order = IMEIOrder(
        id=imei_data.get('id', ''),
        imei=imei_data.get('imei', ''),
        package=imei_data.get('package', ''),
        status=imei_data.get('status', ''),
        code=imei_data.get('code'),
        requested_at=imei_data.get('requestedat'),
        # Parsed fields:
        carrier=parsed_fields.get('carrier'),
        model=parsed_fields.get('model'),
        simlock=parsed_fields.get('simlock'),
        fmi=parsed_fields.get('fmi'),
        imei2=parsed_fields.get('imei2'),
        result_code=parsed_fields.get('result_code'),
        result_code_display=parsed_fields.get('result_code_display')
    )
    orders.append(order)
```

---

### Phase 2: Fix Template Variable

**File:** web_app.py

**Change Required:** Add search_count calculation (line 863-885)

**Before:**
```python
if search_imei:
    # Parse multiple IMEIs
    imeis = [line.strip() for line in search_imei.split('\n')
            if line.strip() and line.strip().isdigit() and len(line.strip()) == 15]

    if len(imeis) == 1:
        orders = db.search_orders_by_imei(imeis[0])
    elif len(imeis) > 1:
        # Search multiple IMEIs
        all_orders = []
        for imei in imeis:
            all_orders.extend(db.search_orders_by_imei(imei))
        orders = all_orders
    else:
        orders = []
        flash('No valid IMEIs found', 'warning')
else:
    orders = db.get_recent_orders(limit=100)

return render_template('history.html',
                     orders=orders,
                     search_query=search_imei)  # ❌ Missing search_count
```

**After:**
```python
if search_imei:
    # Parse multiple IMEIs
    imeis = [line.strip() for line in search_imei.split('\n')
            if line.strip() and line.strip().isdigit() and len(line.strip()) == 15]

    if len(imeis) == 1:
        orders = db.search_orders_by_imei(imeis[0])
    elif len(imeis) > 1:
        # Search multiple IMEIs
        all_orders = []
        for imei in imeis:
            all_orders.extend(db.search_orders_by_imei(imei))
        orders = all_orders
    else:
        orders = []
        flash('No valid IMEIs found', 'warning')
    
    search_count = len(imeis)  # ✅ ADD THIS LINE
else:
    orders = db.get_recent_orders(limit=100)
    search_count = 0  # ✅ ADD THIS LINE

return render_template('history.html',
                     orders=orders,
                     search_query=search_imei,
                     search_count=search_count)  # ✅ ADD THIS PARAMETER
```

---

## Edge Cases & Backward Compatibility

### Edge Case 1: API Returns No Code Field
**Scenario:** Order is still pending, no results yet
**Handling:** All new fields default to None (already handled by Optional[str] = None)

### Edge Case 2: Code Field Has Unexpected Format
**Scenario:** API changes format or returns error message in code
**Handling:** Parsing fails gracefully, fields stay None
**Test:** Add try/except around split() operations

### Edge Case 3: Partial Code Field
**Scenario:** Only some fields present (e.g., only Carrier, no Model)
**Handling:** Each field extracted independently, missing ones = None
**Status:** ✅ Already handled by current design

### Edge Case 4: HTML Entities
**Scenario:** Code contains &lt;, &gt;, &amp;
**Handling:** clean_html() function handles common entities
**Test:** Verify with actual API responses

### Edge Case 5: Old Database Records
**Scenario:** Existing orders with NULL in new fields
**Handling:** Templates already use `or ''` / `or 'N/A'`
**Status:** ✅ Already compatible

---

## Testing Strategy

### Unit Tests (test_client.py)

1. **Test IMEIOrder with all fields**
```python
def test_imei_order_with_parsed_fields():
    order = IMEIOrder(
        id="12345",
        imei="353978109238980",
        package="iPhone Carrier & Simlock USA AT&T",
        status="Completed",
        code="Carrier: T-Mobile<br>SimLock: Unlocked<br>Model: iPhone 12",
        requested_at="2025-11-15 10:00:00",
        carrier="T-Mobile",
        model="iPhone 12",
        simlock="Unlocked",
        fmi="OFF",
        imei2=None,
        result_code="Carrier: T-Mobile<br>SimLock: Unlocked<br>Model: iPhone 12",
        result_code_display="Carrier: T-Mobile\nSimLock: Unlocked\nModel: iPhone 12"
    )
    assert order.carrier == "T-Mobile"
    assert order.model == "iPhone 12"
```

2. **Test _parse_code_field with various formats**
```python
def test_parse_code_field():
    client = GSMFusionClient()
    
    # Test full code
    code = "Carrier: T-Mobile<br>SimLock: Unlocked<br>Model: iPhone 12 Pro<br>Find My iPhone: OFF<br>IMEI2 Number: 355804085587571"
    result = client._parse_code_field(code)
    assert result['carrier'] == "T-Mobile"
    assert result['simlock'] == "Unlocked"
    assert result['model'] == "iPhone 12 Pro"
    assert result['fmi'] == "OFF"
    assert result['imei2'] == "355804085587571"
    
    # Test partial code
    code = "Carrier: Verizon<br>Model: iPhone 13"
    result = client._parse_code_field(code)
    assert result['carrier'] == "Verizon"
    assert result['model'] == "iPhone 13"
    assert result.get('simlock') is None
    
    # Test empty code
    result = client._parse_code_field(None)
    assert result == {}
```

3. **Test get_imei_orders with real API**
```python
def test_get_imei_orders_with_parsed_fields():
    client = GSMFusionClient()
    orders = client.get_imei_orders("15580047")  # The failing order
    
    assert len(orders) > 0
    order = orders[0]
    
    # Basic fields
    assert order.id
    assert order.imei
    assert order.status
    
    # Parsed fields (may be None if pending)
    assert hasattr(order, 'carrier')
    assert hasattr(order, 'model')
    assert hasattr(order, 'simlock')
    assert hasattr(order, 'fmi')
    assert hasattr(order, 'result_code')
    assert hasattr(order, 'result_code_display')
```

### Integration Tests

1. **Test order sync with new fields**
```bash
# Run manual_sync.py - should work identically
python3 manual_sync.py
```

2. **Test web_app.py /history/sync route**
- Create pending orders
- Call /history/sync
- Verify database updated with parsed fields

3. **Test history search with multiple IMEIs**
- Search for 3+ IMEIs
- Verify search_count displays correctly
- No template errors

### Production Validation

1. **Deploy to Railway**
2. **Trigger sync for order 15580047**
3. **Check logs for:**
   - ✅ No AttributeError
   - ✅ Database UPDATE successful
   - ✅ All 6 fields populated

---

## Rollback Plan

### If Phase 1 Fails (IMEIOrder changes)

**Symptoms:**
- get_imei_orders() raises exceptions
- Parsing errors in logs

**Rollback:**
```bash
git revert HEAD
git push -f origin main
```

**Alternative:** Comment out parsing logic, keep fields as None
```python
# Quick disable:
parsed_fields = {}  # Skip parsing temporarily
```

### If Phase 2 Fails (Template changes)

**Symptoms:**
- History page crashes
- Jinja2 template errors

**Rollback:** Remove search_count from template
```html
<!-- Simplified fallback -->
Showing {{ orders|length }} order(s)
```

---

## Dependencies & Side Effects

### Files That Use IMEIOrder

1. **gsm_fusion_client.py** - ✅ Will be updated
2. **web_app.py:927, 1002** - ✅ Will benefit from new fields
3. **batch_processor.py:29, 309** - ⚠️ Check compatibility
4. **manual_sync.py:34** - ✅ Already parses code field (can be simplified)
5. **gsm_cli.py:128** - ✅ Should work (uses basic fields)

### Database Queries Affected

1. **web_app.py:932-952** - ✅ Primary fix target
2. **manual_sync.py:90-96** - ⚠️ Can simplify (parsing now in client)
3. **database.py:152-216** - ✅ No changes needed

### Templates Affected

1. **history.html:45** - ✅ Primary fix target
2. **database.html:104** - ✅ Already compatible (uses `or`)
3. **database_order_detail.html:65-95** - ✅ Already compatible

---

## Deployment Sequence

### Step 1: Pre-deployment Checks
- [ ] Backup imei_orders.db
- [ ] Review current Railway logs for baseline errors
- [ ] Note current order count in database

### Step 2: Code Changes
- [ ] Update gsm_fusion_client.py (IMEIOrder + parsing)
- [ ] Update web_app.py (search_count)
- [ ] Run local tests
- [ ] Commit with descriptive message

### Step 3: Deployment
- [ ] Push to Railway
- [ ] Monitor deployment logs
- [ ] Check health endpoint: /health
- [ ] Verify services load: /

### Step 4: Validation
- [ ] Trigger sync: /history/sync
- [ ] Check Railway logs for:
  - ✅ No AttributeError
  - ✅ UPDATE statements successful
  - ✅ Parsed fields populated
- [ ] Search multiple IMEIs in /history
- [ ] Verify search_count displays

### Step 5: Production Smoke Test
- [ ] Submit new test order
- [ ] Wait for completion
- [ ] Sync and verify all fields populated
- [ ] Export CSV and verify format

---

## Success Criteria

### Must Have (P0)
- ✅ No AttributeError on order.carrier, order.model, etc.
- ✅ Order 15580047 syncs successfully
- ✅ History page loads without template errors
- ✅ Database UPDATE statements execute

### Should Have (P1)
- ✅ Parsed fields (carrier, model, etc.) populated from code field
- ✅ search_count displays correctly for multi-IMEI searches
- ✅ CSV exports include all fields

### Nice to Have (P2)
- ⚠️ Simplify manual_sync.py (remove duplicate parsing)
- ⚠️ Add unit tests for _parse_code_field
- ⚠️ Document code field format in API docs

---

## Timeline Estimate

- **Phase 1 (IMEIOrder):** 30 minutes coding + 15 minutes testing = 45 min
- **Phase 2 (Template):** 5 minutes coding + 5 minutes testing = 10 min
- **Testing:** 20 minutes (local + Railway validation) = 20 min
- **Documentation:** 10 minutes = 10 min

**Total:** ~90 minutes

---

## Open Questions

1. **Q:** Should we simplify manual_sync.py to use the new IMEIOrder fields?
   **A:** YES - Phase 3 cleanup task (not blocking)

2. **Q:** Do we need to handle international characters in code field?
   **A:** Current clean_html() should handle UTF-8, monitor production

3. **Q:** Should result_code and result_code_display both be stored?
   **A:** YES - original for debugging, display for UI (current design correct)

4. **Q:** What if API changes code format in future?
   **A:** Parsing gracefully fails, fields = None, UI shows 'N/A'

---

## Related Issues

### Issue #1: Batch Submission (3 IMEIs → only 1 saved)
**Status:** Separate issue, tracked in BATCH_SUBMISSION_DEBUG.md
**Priority:** P1 (after this fix)

### Issue #2: Supabase Tables Not Created
**Status:** Schema needs to be run in Supabase dashboard
**Priority:** P2 (Railway SQLite works, Supabase is backup)

---

## Contact & Support

**Production Logs:** Railway dashboard → Deployments → View Logs
**Database:** Railway shell → `sqlite3 imei_orders.db`
**API Docs:** GSM_Fusion_API.pdf

---

## Appendix A: Example API Response

**Pending Order:**
```xml
<imeis>
    <id>15580047</id>
    <imei>353978109238980</imei>
    <package>iPhone Carrier & Simlock USA AT&T</package>
    <status>Pending</status>
    <code></code>
    <requestedat>2025-11-15 10:00:00</requestedat>
</imeis>
```

**Completed Order:**
```xml
<imeis>
    <id>15580047</id>
    <imei>353978109238980</imei>
    <package>iPhone Carrier & Simlock USA AT&T</package>
    <status>Completed</status>
    <code>Carrier: T-Mobile<br>SimLock: Unlocked<br>Model: iPhone 12 Pro<br>Find My iPhone: OFF<br>IMEI2 Number: 355804085587571</code>
    <requestedat>2025-11-15 10:00:00</requestedat>
</imeis>
```

---

## Appendix B: File Locations

```
/Users/brandonin/Desktop/HAMMER-API/
├── gsm_fusion_client.py      # Line 41-48: IMEIOrder dataclass
│                              # Line 499-560: get_imei_orders()
├── web_app.py                 # Line 863-885: history() function
│                              # Line 927-952: sync_orders() function
├── database.py                # Line 39-60: orders table schema
├── templates/
│   └── history.html          # Line 45: search_count reference
└── manual_sync.py            # Line 45-87: Reference parsing logic
```

---

## Version History

- **v1.0** (2025-11-15): Initial comprehensive analysis
- Location: PRODUCTION_ERROR_FIX_PLAN.md

---

**END OF DOCUMENT**
