# 🚀 QUICK RESUME - Hammer Fusion API

## ⚡ When You Have Your API Key

### Step 1: Update Config (30 seconds)
```bash
cd /Users/brandonin/Desktop/HAMMER-API
nano .env
# Replace: GSM_FUSION_API_KEY=C0H6-T2S9-H9A0-G0T9-X3N7
# With: GSM_FUSION_API_KEY=YOUR-REAL-KEY
# Save: Ctrl+X, Y, Enter
```

### Step 2: Test (30 seconds)
```bash
export GSM_FUSION_API_KEY=YOUR-REAL-KEY
export GSM_FUSION_USERNAME=scalmobile
export GSM_FUSION_BASE_URL=https://hammerfusion.com
python3 test_client.py
```

### Step 3: Batch Submit (2 minutes)
```bash
# List services first
python3 gsm_cli.py services

# Create CSV
cat > orders.csv << EOF
imei,network_id,model_no
123456789012345,SERVICE_ID,iPhone 12
EOF

# Submit batch
python3 gsm_cli.py batch orders.csv --output results.json

# Check results
cat results.json
```

---

## 📧 Get API Key From:

**Option 1:** Gmail email from today (7:50 AM) with the PDF/ZIP attachments
**Option 2:** https://hammerfusion.com/ticket.php → "Request API Key"
**Option 3:** Contact support with username: scalmobile

---

## 📋 Current Status

- ✅ All code complete and tested
- ✅ Environment configured
- ✅ Dependencies installed
- ❌ **Need valid API key**

**Blocker:** `C0H6-T2S9-H9A0-G0T9-X3N7` is a placeholder, not real

---

## 📞 When Ready

Say: **"I have my API key: XXXX-XXXX-XXXX-XXXX-XXXX"**

I'll help you:
1. Configure it
2. Test connection
3. Submit your first batch
4. Export results

**Time to operational:** ~5 minutes
