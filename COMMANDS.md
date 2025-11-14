# 🎯 Terminal Commands Reference

## Launch Commands (Use These When Ready)

### Navigate to Project
```bash
cd /Users/brandonin/Desktop/HAMMER-API
```

### Set Environment Variables
```bash
export GSM_FUSION_API_KEY=YOUR-REAL-API-KEY
export GSM_FUSION_USERNAME=scalmobile
export GSM_FUSION_BASE_URL=https://hammerfusion.com
```

### Test Connection
```bash
python3 test_client.py
```

### List Available Services
```bash
python3 gsm_cli.py services
```

### Submit Single IMEI
```bash
python3 gsm_cli.py submit IMEI_NUMBER SERVICE_ID
```

### Batch Process CSV
```bash
python3 gsm_cli.py batch orders.csv --output results.json
```

### Check Order Status
```bash
python3 gsm_cli.py status ORDER_ID
```

### Wait for Completion (Auto-poll)
```bash
python3 gsm_cli.py wait ORDER_ID
```

### View Help
```bash
python3 gsm_cli.py --help
```

---

## CSV Format Example

```csv
imei,network_id,model_no
123456789012345,1,iPhone 12
123456789012346,1,iPhone 13
123456789012347,1,iPhone 14
```

---

## Current Blocker

❌ **Invalid API Key:** `C0H6-T2S9-H9A0-G0T9-X3N7`

**Get real key from:**
1. Original Gmail email (Nov 12, 7:50 AM)
2. Support ticket: https://hammerfusion.com/ticket.php
3. Account dashboard (if API Settings exists)

---

## All Documentation Files

- **API_KEY_SETUP_GUIDE.md** - Complete setup guide
- **QUICK_RESUME.md** - Quick reference when you return
- **COMMANDS.md** - This file (terminal commands)
- **README.md** - Full project documentation
- **QUICKSTART.md** - 5-minute getting started guide

---

Ready to proceed once you have valid API key! 🚀
