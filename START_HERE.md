# 🚀 START HERE - GSM Fusion API Automation

## Quick Setup Commands

Copy and paste these commands in your terminal:

```bash
# 1. Navigate to the project directory
cd ~/Desktop/HAMMER-API

# 2. Run the setup script
./setup.sh
```

If you see "permission denied", make the script executable first:

```bash
chmod +x setup.sh
./setup.sh
```

## After Setup

Once setup is complete, configure your credentials:

```bash
# 1. Copy the example configuration
cp .env.example .env

# 2. Edit the .env file with your credentials
nano .env
```

Add your credentials to `.env`:
```
GSM_FUSION_API_KEY=YOUR-API-KEY-HERE
GSM_FUSION_USERNAME=your_username
GSM_FUSION_BASE_URL=http://hammerfusion.com
```

Save the file (in nano: Ctrl+O, Enter, then Ctrl+X)

## Verify Installation

```bash
# Test the installation
python3 verify_installation.py

# Test API connection
python3 test_client.py
```

## Your First Command

```bash
# List available services
python3 gsm_cli.py services
```

## 📖 Next Steps

Once you've completed setup:

1. **Read:** `GETTING_STARTED.md` - Step-by-step walkthrough
2. **Quick Start:** `QUICKSTART.md` - 5-minute guide
3. **Full Docs:** `README.md` - Complete reference
4. **Examples:** Check the `examples/` folder

## Need Help?

All files are in: `/Users/brandonin/Desktop/HAMMER-API/`

To get there from anywhere:
```bash
cd ~/Desktop/HAMMER-API
```

## Common Commands

```bash
# List services
python3 gsm_cli.py services

# Submit single IMEI
python3 gsm_cli.py submit YOUR_IMEI SERVICE_ID

# Check order status
python3 gsm_cli.py status ORDER_ID

# Batch process from CSV
python3 gsm_cli.py batch orders.csv

# Wait for order completion
python3 gsm_cli.py wait ORDER_ID
```

## File Structure

```
HAMMER-API/                    ← You are here!
├── START_HERE.md             ← This file
├── GETTING_STARTED.md        ← Read this first
├── QUICKSTART.md             ← 5-minute guide
├── README.md                 ← Full documentation
├── setup.sh                  ← Run this to install
├── gsm_cli.py               ← Main CLI tool
├── examples/                 ← Working examples
│   ├── simple_order.py
│   ├── batch_processing.py
│   └── iphone_automation.py
└── .env.example              ← Copy to .env and configure
```

---

## 🎯 Quick Copy-Paste Setup

Just copy and paste this entire block:

```bash
cd ~/Desktop/HAMMER-API
chmod +x setup.sh
./setup.sh
cp .env.example .env
echo "✅ Setup complete! Now edit .env with your credentials:"
echo "   nano .env"
```

Then run:
```bash
nano .env
# Add your API key and username, save and exit
python3 verify_installation.py
```

---

**You're ready to eliminate manual website tasks and automate everything!** 🚀
