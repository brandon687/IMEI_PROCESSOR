# Production Error Fix - Quick Implementation Summary

## Critical Files & Line Numbers

### File 1: gsm_fusion_client.py

**Line 41-48: IMEIOrder dataclass - ADD 7 FIELDS**
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
    # ADD THESE 7 FIELDS:
    carrier: Optional[str] = None
    model: Optional[str] = None
    simlock: Optional[str] = None
    fmi: Optional[str] = None
    imei2: Optional[str] = None
    result_code: Optional[str] = None
    result_code_display: Optional[str] = None
```

**After line 282 (after _xml_to_dict method) - ADD NEW METHOD**
```python
def _parse_code_field(self, code: str) -> Dict[str, str]:
    """Parse HTML-formatted code field into individual attributes"""
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
    cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)
    result['result_code_display'] = cleaned_code.strip()
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

**Line 548-557: get_imei_orders method - REPLACE ORDER CREATION**
```python
# REPLACE:
for imei_data in imeis_data:
    order = IMEIOrder(
        id=imei_data.get('id', ''),
        imei=imei_data.get('imei', ''),
        package=imei_data.get('package', ''),
        status=imei_data.get('status', ''),
        code=imei_data.get('code'),
        requested_at=imei_data.get('requestedat')
    )
    orders.append(order)

# WITH:
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

### File 2: web_app.py

**Line 863-892: history function - ADD search_count VARIABLE**

**FIND THIS BLOCK (around line 863-891):**
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
                     search_query=search_imei)
```

**REPLACE WITH:**
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

## Testing Checklist

### Local Testing
- [ ] Run: `python3 -c "from gsm_fusion_client import IMEIOrder; print(IMEIOrder.__dataclass_fields__.keys())"`
- [ ] Verify output includes: carrier, model, simlock, fmi, result_code, result_code_display
- [ ] Run: `python3 web_app.py`
- [ ] Visit: http://localhost:5001/history
- [ ] Search multiple IMEIs - should show "Showing X order(s) for Y IMEIs searched"

### Production Testing (Railway)
- [ ] Push to Railway: `git push origin working-version-restore`
- [ ] Monitor logs for deployment success
- [ ] Visit Railway URL: /history/sync
- [ ] Check logs for: "✅ Synced X orders successfully" (no AttributeError)
- [ ] Query failing order: Visit /status/15580047
- [ ] Verify all fields populated

---

## Expected Changes Summary

**gsm_fusion_client.py:**
- IMEIOrder: 6 fields → 13 fields (+7)
- New method: _parse_code_field() (~60 lines)
- Modified: get_imei_orders() order creation loop

**web_app.py:**
- Modified: history() function (3 lines added)

**Total LOC:** ~70 lines added/modified across 2 files

---

## Validation Commands

```bash
# Check IMEIOrder has new fields
python3 -c "from gsm_fusion_client import IMEIOrder; o = IMEIOrder('1','2','3','4'); print('carrier' in dir(o))"

# Test parsing function exists
python3 -c "from gsm_fusion_client import GSMFusionClient; c = GSMFusionClient(); print(hasattr(c, '_parse_code_field'))"

# Check web_app.py syntax
python3 -m py_compile web_app.py

# Run quick API test
python3 -c "from gsm_fusion_client import GSMFusionClient; c = GSMFusionClient(); orders = c.get_imei_orders('15580047'); print(f'Fields: carrier={hasattr(orders[0], \"carrier\")}, model={hasattr(orders[0], \"model\")}')"
```

---

## Rollback Command

```bash
# If anything goes wrong:
git revert HEAD
git push -f origin working-version-restore
```

---

**END OF IMPLEMENTATION SUMMARY**
