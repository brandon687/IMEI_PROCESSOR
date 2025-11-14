# 📋 Handling Duplicate IMEIs - Complete Guide

## 🎯 Your Business Need

You need to **recheck IMEIs** for legitimate reasons:
- ✅ Verify iCloud sign-out after customer return
- ✅ Confirm unlock status changed (locked → unlocked)
- ✅ Recheck device after repairs
- ✅ Validate status before resale

## 🔒 Why Duplicates Are Blocked

**Hammer Fusion's API blocks duplicate IMEI submissions** to:
- Prevent double-charging customers
- Avoid wasting credits on the same check
- Maintain clean order history
- Prevent system abuse

**This is intentional and cannot be overridden via the API.**

---

## ✅ **Solution: View Existing Order Results**

Instead of resubmitting, **look up the original order** to see the results!

### Why This Works Better:
1. **No additional cost** - View existing results for free
2. **Instant access** - No waiting for new order
3. **Historical tracking** - See when device was originally checked
4. **Complete data** - All original results still available

---

## 📊 How to Access Existing Orders

### **Method 1: Hammer Fusion Website (Recommended)**

1. **Login to**: https://hammerfusion.com
2. **Navigate to**: Orders → IMEI Orders
   Direct link: https://hammerfusion.com/imeiorders.php
3. **Search or Filter**:
   - Use browser search (Ctrl+F / Cmd+F) to find IMEI
   - Sort by date to find recent orders
   - Filter by status (Completed, Pending, Rejected)

**What You See:**
- Order ID
- IMEI
- Service used
- Status
- Complete results in "Code" column
- Submission date/time

**Example:**
```
Order #15556534
IMEI: 353370080089458
Status: Completed
Results: [Full device information displayed]
```

---

### **Method 2: Local Order History (Recent Only)**

1. **Open**: http://localhost:5001/history
2. **View**: Last 10 orders submitted via web interface
3. **Click "View Details"** on any order
4. **See**: Order ID, IMEI, Status, Results

**Note:** This only shows orders submitted through the web interface during current session.

---

### **Method 3: CLI Status Check (If You Have Order ID)**

If you know the Order ID:
```bash
python3 gsm_cli.py status <ORDER_ID>
```

Example:
```bash
python3 gsm_cli.py status 15556534
```

**Output:**
```
Order ID: 15556534
IMEI: 353370080089458
Status: Completed
Package: Apple iPhone Checker
Code: [Full results]
```

---

## 🔄 Real-World Workflow Examples

### **Scenario 1: Customer Return - Verify iCloud Sign-Out**

**Situation:** Customer returned iPhone, need to verify iCloud is removed before resale.

**Steps:**
1. Go to https://hammerfusion.com/imeiorders.php
2. Search for device IMEI (Ctrl+F)
3. View original order results
4. Check "Find My iPhone" status in results
5. ✅ If OFF - Ready to resell
6. ❌ If ON - Contact customer

**No new order needed! Original results show iCloud status.**

---

### **Scenario 2: Device Unlocked - Verify Status Changed**

**Situation:** Device was locked, sent to unlock service, need to verify it's now unlocked.

**Option A - Check Original Order:**
```
1. Find original IMEI check order
2. Look at "Simlock" status
3. Compare with unlock service confirmation
```

**Option B - Submit NEW Order (Fresh Check):**
```
1. Use different service/carrier if available
2. Or contact Hammer Fusion support to request re-check
3. Some unlock services include post-unlock verification
```

---

### **Scenario 3: Quality Control - Batch Device Verification**

**Situation:** Need to verify multiple returned devices.

**Best Practice:**
1. **Export order history** from Hammer Fusion website
2. **Match IMEIs** from your inventory to orders
3. **Review results** in bulk
4. **Flag devices** that need attention

---

## 💡 Workarounds for True Re-Checks

If you **absolutely must** submit the same IMEI again:

### **Option 1: Contact Hammer Fusion Support**
- Email/ticket explaining legitimate business need
- They may manually reset the IMEI in their system
- Or provide alternative solution

### **Option 2: Use Different Service**
- If you used Service A (e.g., AT&T checker)
- Try Service B (e.g., Universal checker)
- Different services may allow same IMEI

### **Option 3: Wait for System Reset**
- Some services may allow re-submission after time period
- Check with Hammer Fusion for their policies

### **Option 4: API Key from Different Account**
- If you have multiple Hammer Fusion accounts
- Same IMEI can be checked on different account
- But this costs credits on each account

---

## 🎓 Best Practices

### **1. Track Your Orders**
Keep a spreadsheet with:
- IMEI
- Order ID
- Date submitted
- Service used
- Results summary
- Device status

### **2. Use Order History First**
Before submitting:
1. Check if IMEI was already submitted
2. Review existing results
3. Only submit if truly new check is needed

### **3. Understand Service Differences**
Some services provide:
- One-time check (results don't change)
- Real-time status (check again for updates)
- Historical data (shows status over time)

Ask Hammer Fusion which services support re-checks.

### **4. Document Your Process**
For compliance/quality control:
- Screenshot original order results
- Save Order IDs for each device
- Note when device was checked
- Track status changes

---

## 🔧 Updated Web Interface Features

### **What We Added:**

1. **Better Error Messages**
   - Clear explanation when duplicate detected
   - Link to order history
   - Instructions to view existing results

2. **Information Card on Submit Page**
   - Explains why duplicates are blocked
   - Shows where to find existing orders
   - Provides direct links

3. **Improved Workflow**
   - Submit page → Duplicate error → Directed to history
   - Clear next steps for users
   - No confusion about "failed" vs "duplicate"

---

## 📋 Quick Reference

| Need | Action | Location |
|------|--------|----------|
| **View all orders** | Check Hammer Fusion website | https://hammerfusion.com/imeiorders.php |
| **Find specific IMEI** | Search on website (Ctrl+F) | Order history page |
| **Recent submissions** | Check local history | http://localhost:5001/history |
| **Order by ID** | Use CLI status command | `python3 gsm_cli.py status <ID>` |
| **Bulk export** | Export from website | Use Hammer Fusion's export feature |
| **Re-check needed** | Contact support | Hammer Fusion support ticket |

---

## ⚠️ Important Notes

1. **Original results remain valid** - Device specs don't change
2. **Status CAN change** - Lock/iCloud status may update
3. **Hammer Fusion tracks by account** - Different account = can submit
4. **No API override exists** - This is a server-side restriction
5. **Order history is permanent** - Results never deleted

---

## 🎯 Summary

**For most business needs:**
✅ **View existing order results** instead of resubmitting
✅ Use Hammer Fusion website to search order history
✅ No additional cost, instant access to data

**For true re-checks:**
❌ API doesn't support override
✅ Contact Hammer Fusion support for special cases
✅ Use different services if available
✅ Track orders carefully to avoid duplicates

---

## 🚀 Quick Start

**To view existing IMEI results:**
1. Go to https://hammerfusion.com/imeiorders.php
2. Login with your credentials
3. Press Ctrl+F (Windows) or Cmd+F (Mac)
4. Type the IMEI you're looking for
5. View the order results

**To prevent duplicate submissions:**
1. Check order history BEFORE submitting
2. Use our web interface at http://localhost:5001
3. Review "Recent Orders" to see what's already submitted
4. Follow the helpful links when duplicate detected

---

**Need more help? Contact Hammer Fusion support with your specific use case!**
