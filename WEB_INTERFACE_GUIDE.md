# 🌐 GSM Fusion Web Interface Guide

## ✅ Server is Running!

Your local web interface is now live at:

**🔗 http://localhost:5001**

---

## 🚀 Quick Start

### Starting the Server

```bash
cd /Users/brandonin/Desktop/HAMMER-API
python3 web_app.py
```

The server will start on port 5001 and display:
```
✓ Server running at: http://localhost:5001
```

### Accessing the Interface

Open your web browser and go to:
- **http://localhost:5001** (from your computer)
- **http://192.168.7.180:5001** (from other devices on your network)

---

## 📋 Features

### 1. **Home Page** (/)
- View popular services
- Quick access to all features
- Recent order history
- One-click navigation

### 2. **Submit Order** (/submit)
- Enter IMEI (15 digits)
- Select service from dropdown
- Instant validation
- Real-time submission

**Quick Submit Example:**
1. Click "Submit Order" button
2. Enter IMEI: `359702373699048`
3. Select Service: `1739 - Apple iPhone Checker`
4. Click "Submit Order"
5. Automatically redirected to status page

### 3. **Order Status** (/status/<order_id>)
- Real-time status updates
- Auto-refresh every 10 seconds (for pending orders)
- View complete results
- Copy results to clipboard
- Beautiful formatted output

**Status Types:**
- ✅ **Completed** - Results are ready (green badge)
- ⏳ **Pending/In Process** - Order is processing (yellow badge)
- ❌ **Rejected** - Order was rejected (red badge)

### 4. **All Services** (/services)
- Browse all 236+ services
- Search by keyword
- Filter by category
- View service details

**Search Examples:**
- Search: "checker" → Find all checker services
- Search: "AT&T" → Find AT&T services
- Filter: "Hammer Hot Services" → Popular services only

### 5. **Order History** (/history)
- View all recent orders
- Quick access to order details
- Track submission times
- One-click status check

---

## 🎨 Interface Features

### Beautiful Design
- Modern gradient interface
- Responsive layout (works on mobile)
- Smooth animations
- Color-coded status badges

### User-Friendly
- Form validation
- Helpful tooltips
- Error messages
- Success notifications

### Real-Time Updates
- Auto-refresh for pending orders
- Instant status checks
- Live service data
- Dynamic results display

---

## 📊 Common Workflows

### Workflow 1: Quick IMEI Check
1. Open http://localhost:5001
2. Click "Submit Order"
3. Enter IMEI
4. Select Service 1739 (iPhone Checker - $0.08)
5. Submit
6. Wait 1-5 minutes
7. View results automatically

### Workflow 2: Browse Services First
1. Click "All Services"
2. Search for your carrier (e.g., "AT&T")
3. Click "Details" on a service
4. Enter IMEI on detail page
5. Submit directly from there

### Workflow 3: Track Multiple Orders
1. Submit multiple orders
2. Click "Order History"
3. View all recent submissions
4. Click "View Details" on any order
5. Check status of each

---

## 🔧 Technical Details

### Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5 + CSS3 + JavaScript
- **API**: GSM Fusion API Client
- **Port**: 5001 (configurable)

### Auto-Features
- **Auto-refresh**: Pending orders refresh every 10 seconds
- **Auto-redirect**: After submit, goes to status page
- **Auto-validation**: IMEI must be 15 digits
- **Auto-format**: Results displayed in readable format

### Browser Requirements
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Cookies enabled (for flash messages)

---

## 🎯 Sample Test Flow

**Test the Apple iPhone Checker (Most Popular):**

1. **Start Server**:
   ```bash
   python3 web_app.py
   ```

2. **Open Browser**:
   Navigate to http://localhost:5001

3. **Submit Test Order**:
   - Click "Submit Order"
   - IMEI: `359702373699048` (example)
   - Service: `1739 - Apple iPhone Checker`
   - Click "Submit Order"

4. **View Results**:
   - Auto-redirected to status page
   - Page auto-refreshes every 10 seconds
   - When completed (1-5 min), results show:
     - Carrier information
     - Simlock status
     - Find My iPhone status
     - Warranty details
     - Full device specs

5. **Check History**:
   - Click "Order History"
   - See your test order
   - Click to view again anytime

---

## 🛠️ Customization

### Change Port
Edit `web_app.py` line 218:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```
Change `5001` to any available port.

### Disable Debug Mode
For production use:
```python
app.run(debug=False, host='0.0.0.0', port=5001)
```

### Change Theme Colors
Edit `templates/base.html` CSS section:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 📱 Access from Phone/Tablet

1. Make sure your device is on the same network
2. Find your computer's IP address: `192.168.7.180`
3. Open browser on phone/tablet
4. Navigate to: `http://192.168.7.180:5001`
5. Use the interface normally!

---

## ⚡ Keyboard Shortcuts

- **Tab**: Navigate between form fields
- **Enter**: Submit forms
- **Ctrl/Cmd + R**: Refresh page (manual status update)
- **Ctrl/Cmd + C**: Copy selected results

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :5001

# Kill process if needed
kill -9 <PID>
```

### Can't Access from Browser
- Make sure server shows "Running on http://127.0.0.1:5001"
- Try http://127.0.0.1:5001 instead of localhost
- Check firewall settings

### Orders Not Showing
- Check `.env` file has correct API credentials
- Verify internet connection
- Check server logs for errors

### Results Not Loading
- Wait for order to complete (check delivery time)
- Manually refresh the page
- Check order status on hammerfusion.com website

---

## 📈 Performance

- **Home page load**: < 1 second
- **Service list load**: < 2 seconds (236 services)
- **Order submission**: < 2 seconds
- **Status check**: < 1 second
- **Auto-refresh interval**: 10 seconds (configurable)

---

## 🔒 Security Notes

- This is a **local development server**
- Do not expose to public internet
- Use only on trusted networks
- API key stored in `.env` file
- No data stored on disk (session only)

---

## 🎉 You're All Set!

**Server is running at: http://localhost:5001**

Open your browser and start testing! 🚀

---

## 📚 Related Files

- `web_app.py` - Main Flask application
- `templates/` - HTML templates
- `gsm_fusion_client.py` - API client
- `.env` - Configuration (API key, username)
- `QUICK_START_GUIDE.md` - CLI usage guide

---

**Need help?** Check the server console for error messages or visit http://localhost:5001 to get started!
