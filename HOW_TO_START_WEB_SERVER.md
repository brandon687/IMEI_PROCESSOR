# 🚀 How to Start the Web Server

## ✅ Server is Currently Running!

**The server is LIVE at:**
- http://localhost:5001
- http://127.0.0.1:5001
- http://192.168.7.180:5001 (from other devices)

**Process ID:** Check with `ps aux | grep web_app.py`

---

## 🔄 If You Need to Restart the Server

### Method 1: Quick Start (Recommended)

```bash
cd /Users/brandonin/Desktop/HAMMER-API
python3 web_app.py
```

**Keep this terminal window open!** The server runs in this window.

---

### Method 2: Background Process (Current Setup)

```bash
cd /Users/brandonin/Desktop/HAMMER-API

# Start in background
nohup python3 web_app.py > web_app.log 2>&1 &

# View logs
tail -f web_app.log

# Check if running
ps aux | grep web_app.py

# Stop server
pkill -f web_app.py
```

---

## 🔍 Troubleshooting

### Problem: "This site can't be reached" or "ERR_CONNECTION_REFUSED"

**Cause:** Server is not running

**Solution:**
1. Open Terminal
2. Navigate to project: `cd /Users/brandonin/Desktop/HAMMER-API`
3. Start server: `python3 web_app.py`
4. Keep terminal window open
5. Open browser to http://localhost:5001

---

### Problem: "Address already in use"

**Cause:** Port 5001 is already in use

**Solution:**
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Or use a different port (edit web_app.py line 218)
```

---

### Problem: Page loads but shows errors

**Cause:** Missing dependencies or API issues

**Solution:**
```bash
# Check logs
tail -50 web_app.log

# Verify .env file has correct credentials
cat .env

# Test API connection
python3 -c "from gsm_fusion_client import GSMFusionClient; c = GSMFusionClient(); print('API OK')"
```

---

## ✅ Verify Server is Running

### Method 1: Browser
Open http://localhost:5001 - You should see the homepage

### Method 2: Terminal
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001
# Should return: 200
```

### Method 3: Check Process
```bash
ps aux | grep web_app.py
# Should show the running process
```

### Method 4: Check Logs
```bash
tail web_app.log
# Should show "Running on http://127.0.0.1:5001"
```

---

## 📋 Expected Server Output

When you start the server, you should see:

```
================================================================================
GSM FUSION WEB INTERFACE
================================================================================

✓ Starting web server...
✓ Server running at: http://localhost:5001

Press CTRL+C to stop the server

================================================================================
 * Serving Flask app 'web_app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.7.180:5001
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

---

## 🎯 Step-by-Step: Fresh Start

If nothing is working, follow these steps exactly:

### Step 1: Stop Any Running Servers
```bash
pkill -f web_app.py
```

### Step 2: Navigate to Project
```bash
cd /Users/brandonin/Desktop/HAMMER-API
```

### Step 3: Verify Files Exist
```bash
ls -la web_app.py templates/ .env
```

### Step 4: Start Server (Keep Terminal Open!)
```bash
python3 web_app.py
```

### Step 5: Wait for Startup Message
Look for: "✓ Server running at: http://localhost:5001"

### Step 6: Open Browser
Navigate to: http://localhost:5001

### Step 7: You Should See
- Purple gradient header
- "GSM Fusion API Tester" title
- Navigation menu
- Popular services list

---

## 🖥️ Keeping Server Running

### Option A: Foreground (Simple)
- Run `python3 web_app.py`
- Keep terminal open
- Press Ctrl+C to stop

### Option B: Background (Advanced)
- Run `nohup python3 web_app.py > web_app.log 2>&1 &`
- Terminal can be closed
- Use `pkill -f web_app.py` to stop

### Option C: Screen/tmux (Professional)
```bash
# Install screen (if needed)
# brew install screen

# Start screen session
screen -S webserver

# Run server
python3 web_app.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r webserver
```

---

## 📱 Accessing from Other Devices

1. Find your computer's IP: `192.168.7.180` (shown in server output)
2. Make sure device is on same network
3. Open browser on phone/tablet
4. Navigate to: `http://192.168.7.180:5001`

---

## ⚠️ Important Notes

1. **Keep Terminal Open** (if running in foreground)
2. **Check .env file** has correct API credentials
3. **Port 5001** must be available
4. **Internet connection** required for API calls
5. **Python 3.9+** required

---

## 🔧 Quick Commands Reference

```bash
# Start server
python3 web_app.py

# Start in background
nohup python3 web_app.py > web_app.log 2>&1 &

# Stop server
pkill -f web_app.py

# View logs
tail -f web_app.log

# Check if running
ps aux | grep web_app.py
curl http://localhost:5001

# Test API connection
python3 gsm_cli.py services | head -10
```

---

## ✅ Current Status

**Right now, your server IS running!**

Just open your browser and go to:
**http://localhost:5001**

If you see "connection refused", the server stopped. Just run:
```bash
python3 web_app.py
```

And keep the terminal open!

---

## 🎉 What You'll See

When you open http://localhost:5001, you'll see:

1. **Home Page** with:
   - Welcome message
   - Quick action cards (Submit, Browse, History)
   - Popular services table
   - Recent orders

2. **Navigation Menu**:
   - 🏠 Home
   - 📋 All Services
   - 🚀 Submit Order
   - 📊 Recent Orders

3. **Submit Page**: Form to submit IMEI orders

4. **Status Page**: Real-time order tracking

5. **Services Page**: Browse all 236+ services

---

**Need help? Check web_app.log for error messages!**
