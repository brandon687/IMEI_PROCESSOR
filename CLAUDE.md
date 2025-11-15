# HAMMER-API Project Memory

---

## 🚨 CRITICAL: WORKING VERSION BASELINE - READ THIS FIRST

### Functional Project #1 - Production Baseline
**Date Established**: November 15, 2025
**Commit**: `3a7f0e9` (working-version-restore branch)
**Status**: ✅ VERIFIED WORKING IN PRODUCTION

### Emergency Rollback Command
```bash
git checkout 3a7f0e9
git checkout -b emergency-restore
git push -f origin emergency-restore:main
```

### What Makes This Version Work
- **File Structure**: FLAT - all Python files at root (no src/ directory)
- **Entry Point**: `web_app:app` (not `src.web_app:app`)
- **Procfile**: `gunicorn web_app:app --bind 0.0.0.0:$PORT ...`
- **No Package Structure**: Simple direct imports, no __init__.py needed
- **Railway**: Deploys successfully with NIXPACKS builder

### What Breaks This Version
- Moving files to src/ directory without proper package setup
- Changing Procfile to src.web_app:app without creating __init__.py
- Any reorganization without testing Railway deployment first
- Updating entry points in some configs but not others

**📄 Full Documentation**: `WORKING_VERSION_BASELINE.md` (contains complete revert instructions)

---

## Project Overview

**HAMMER-API** is a professional Python-based IMEI verification and GSX data retrieval system that interfaces with the GSM Fusion API (hammerfusion.com). The system includes a Flask web interface, production-grade batch processing, and local database caching for order history.

### Core Purpose
- Automate IMEI data processing and verification
- Retrieve Apple GSX details for iPhones
- Process large volumes of IMEIs efficiently (6,000-20,000 daily)
- Provide web interface for easy order submission and tracking

---

## Technology Stack

### Backend
- **Python 3.x** - Primary language
- **Flask** - Web framework for UI
- **SQLite** - Local database (imei_orders.db)
- **Requests** - HTTP client with retry logic

### Dependencies (requirements.txt)
```
requests>=2.31.0
urllib3>=2.0.0
tabulate>=0.9.0
pandas>=2.0.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
tqdm>=4.65.0
```

### External API
- **GSM Fusion API** (hammerfusion.com)
- Authentication: API Key + Username
- Primary endpoints: /imei-services, /placeimeiorder, /getimeis

---

## Architecture

### Core Components

1. **gsm_fusion_client.py** - GSM Fusion API client
   - Professional API wrapper with retry logic
   - Handles authentication and request management
   - Type-safe with dataclasses (IMEIOrder, ServiceInfo)
   - Methods: get_imei_services(), place_imei_order(), get_imei_orders()

2. **web_app.py** - Flask web application
   - Routes: /, /submit, /batch, /history, /database
   - Auto-sync functionality (5-minute intervals)
   - Integrates API client with database
   - Runs on port 5001 by default

3. **database.py** - SQLite database layer
   - IMEIDatabase class for order storage
   - Tables: orders (with full order details)
   - Methods: insert_order(), get_recent_orders(), search_orders_by_imei()
   - Auto-sync capability for pending orders

4. **production_submission_system.py** - Enterprise batch processor
   - Handles 6,000-20,000 IMEIs in seconds
   - Atomic transactions with rollback
   - Automatic retry with exponential backoff
   - Checkpoint-based crash recovery
   - 96x faster than individual submissions

5. **batch_processor.py** - Original batch processor
   - CSV/Excel file import
   - Progress tracking with callbacks
   - Export to multiple formats

---

## Critical Files & Locations

### Configuration
- `.env` - API credentials (NEVER commit!)
- `.env.example` - Template for credentials
- `imei_orders.db` - SQLite database (persistent storage)

### Main Entry Points
- `web_app.py` - Start web server
- `gsm_cli.py` - Command-line interface
- `START_WEB_INTERFACE.sh` - Quick start script

### Documentation (LOTS of it!)
- `README.md` - Main documentation
- `ARCHITECTURE.txt` - System architecture diagram
- `GETTING_STARTED.md` - Setup guide
- `ORDER_HISTORY_GUIDE.md` - Database integration guide
- `PRODUCTION_INTEGRATION.md` - Production system details
- `20K_SUBMISSION_GUIDE.md` - Large-scale batch processing
- `CRITICAL_COST_SAFEGUARDS.md` - Cost protection measures

---

## Environment Variables

Required in `.env`:
```bash
GSM_FUSION_API_KEY=XXXX-XXXX-XXXX-XXXX-XXXX
GSM_FUSION_USERNAME=your_username
GSM_FUSION_BASE_URL=http://hammerfusion.com
LOG_LEVEL=INFO
```

---

## Common Commands

### Start Web Interface
```bash
python3 web_app.py
# Access at http://localhost:5001
```

### CLI Usage
```bash
# List services
python3 gsm_cli.py services

# Submit single order
python3 gsm_cli.py submit 123456789012345 1

# Check order status
python3 gsm_cli.py status 12345

# Batch process
python3 gsm_cli.py batch orders.csv --output results.json
```

### Quick Start
```bash
./START_WEB_INTERFACE.sh
```

---

## Database Schema

### orders Table (imei_orders.db)
```sql
- id (INTEGER PK) - Auto-increment
- order_id (TEXT UNIQUE) - GSM Fusion order ID
- service_name (TEXT) - Service display name
- service_id (TEXT) - Service package ID
- imei (TEXT NOT NULL) - 15-digit IMEI
- imei2 (TEXT) - Dual-SIM IMEI2
- credits (REAL) - Cost in credits
- status (TEXT) - Pending/Completed/Rejected/In Process
- carrier (TEXT) - Result: Carrier name
- simlock (TEXT) - Result: Lock status
- model (TEXT) - Result: Device model
- fmi (TEXT) - Find My iPhone status
- order_date (TIMESTAMP) - When order placed
- result_code (TEXT) - SUCCESS, etc.
- notes (TEXT) - Additional info
- raw_response (TEXT) - Full JSON response
- created_at (TIMESTAMP) - Record creation
- updated_at (TIMESTAMP) - Last update
```

---

## Performance Characteristics

### Order Processing
- **Single order**: ~500ms (1 API call)
- **100 orders (batch)**: ~30-60s (100 API calls)
- **6,000 IMEIs (production)**: 8 seconds (60 batch calls)
- **20,000 IMEIs (production)**: 25 seconds (200 batch calls)

### Database Operations (Local, No API)
- **View history (100 orders)**: ~50ms
- **Search by IMEI**: ~10ms
- **Export 1000 orders to CSV**: ~200ms
- **Sync 100 pending orders**: ~1-2s (1 batch API call)

**Key Optimization**: Local database caching reduces API calls by 95%+

---

## API Integration Details

### Order Status Codes
- `1` - Pending
- `2` - Completed
- `3` - Rejected
- `4` - In Process

### Rate Limits
- Typical: 60 requests/minute
- Batch requests count as 1 request
- Status checks usually free/unlimited

### Batch Support
- API accepts multiple order IDs: "12345678,12345679,12345680"
- Single call returns all statuses
- Reduces API calls by 100x for syncing

---

## Production Features

### Reliability
- ✅ Atomic database transactions (all-or-nothing)
- ✅ Automatic retry (3 attempts with exponential backoff)
- ✅ Crash recovery via checkpointing (checkpoint_*.json files)
- ✅ Zero data loss guarantees
- ✅ Duplicate prevention (idempotency)
- ✅ Comprehensive logging (web_app.log, server.log)

### Cost Safeguards
- Pre-flight balance checks
- Cost estimation before submission
- Minimum balance requirements
- Transaction logging

### Auto-Sync
- Runs every 5 minutes by default (AUTO_SYNC_INTERVAL=300)
- Updates pending orders automatically
- Background thread, non-blocking

---

## CSV File Format

For batch processing:
```csv
imei,network_id,model_no,operator_id
123456789012345,1,iPhone 12,
123456789012346,1,iPhone 12,
123456789012347,2,,5
```

**Required**: imei, network_id
**Optional**: model_no, operator_id, service_id, provider_id, etc.

---

## Security Best Practices

1. **Never commit .env** - Already in .gitignore
2. **Treat API keys like passwords**
3. **Use HTTPS when available**
4. **Rotate keys regularly**
5. **Limit credential access**

---

## Error Handling

### GSMFusionAPIError
Custom exception for API errors. Always caught and logged.

### Retry Logic
- Max retries: 3-5 (configurable)
- Exponential backoff: 1s, 2s, 4s, 8s
- Automatic session recreation on failure

### Duplicate IMEI
- API rejects duplicates
- Check database first with search_orders_by_imei()
- Use "force_recheck" flag in web UI to override

---

## Code Patterns & Conventions

### Client Initialization
```python
from gsm_fusion_client import GSMFusionClient

# With context manager (recommended)
with GSMFusionClient() as client:
    services = client.get_imei_services()
    # auto-closes

# Manual
client = GSMFusionClient()
try:
    # work
finally:
    client.close()
```

### Database Operations
```python
from database import get_database

db = get_database()
db.insert_order(order_data)
orders = db.get_recent_orders(limit=100)
results = db.search_orders_by_imei("123456789012345")
```

### Progress Tracking
```python
from batch_processor import BatchProcessor, progress_bar_callback

processor = BatchProcessor(progress_callback=progress_bar_callback)
results = processor.process_batch(orders)
processor.print_summary()
```

---

## Future Integration Plans

### T-Mobile API (In Research Phase)
- Direct carrier API access being explored
- Would complement GSM Fusion data
- See: TMOBILE_PARTNERSHIP_STRATEGY.md
- Architecture supports dual data sources
- Add "source" field to database: 'GSM_FUSION' or 'TMOBILE_DIRECT'

### Planned Features
- Parallel API calls (GSM Fusion + T-Mobile)
- Combined result merging
- EIP balance checking (T-Mobile specific)
- Enhanced carrier lock detection

---

## Testing Files

### Production Tests
- `test_batch_20_imeis.py` - 20 IMEI batch test
- `test_batch_10_fresh.py` - 10 fresh IMEI test
- `validate_integration.py` - Integration validation

### Development Tests
- `comprehensive_api_test.py` - Full API test suite
- `test_client.py` - Basic client tests
- `test_web_interface.py` - Web UI tests
- `test_actual_submission.py` - Real submission test

### Utilities
- `generate_test_imeis.py` - Generate test IMEIs
- `check_if_submitted.py` - Check submission status
- `manual_sync.py` - Manual database sync

---

## Logging

### Log Files
- `web_app.log` - Flask application logs
- `server.log` - Server/API logs
- Console output for CLI tools

### Log Levels
- DEBUG - Verbose API calls
- INFO - Standard operations (default)
- WARNING - Non-critical issues
- ERROR - Critical failures

Set via environment: `LOG_LEVEL=DEBUG python3 web_app.py`

---

## Templates (Web UI)

Located in `templates/` directory:
- `index.html` - Home page with service list
- `submit.html` - Single order submission
- `batch.html` - Batch CSV/Excel upload
- `history.html` - Order history viewer
- `database.html` - Database management/search
- `status.html` - Order status details
- `error.html` - Error display page

Static assets in `static/` (currently empty, uses inline styles)

---

## Checkpoint System

### Purpose
Crash recovery for large batch operations

### Format
JSON files: `checkpoint_<hash>.json`
```json
{
  "batch_id": "uuid",
  "timestamp": "2025-11-14T10:53:00",
  "processed_count": 50,
  "total_count": 100,
  "successful": 48,
  "failed": 2,
  "pending_imeis": ["123...", "456..."]
}
```

### Recovery
Automatically loads checkpoint on restart if found

---

## Important Notes

### NEVER Do This
- ❌ Commit .env file
- ❌ Share API keys publicly
- ❌ Run batch operations without cost checks
- ❌ Submit same IMEI multiple times (wastes credits)
- ❌ Use production API key in tests

### ALWAYS Do This
- ✅ Check database before submitting (duplicate prevention)
- ✅ Use batch operations for multiple IMEIs
- ✅ Monitor logs for errors
- ✅ Verify balance before large batches
- ✅ Test with small batches first

---

## Quick Troubleshooting

### "API key is required"
Set environment variables or create .env file

### "Connection timeout"
Increase timeout: `GSMFusionClient(timeout=60)`

### "Duplicate IMEI"
IMEI already submitted. Check history: `/database/search`

### "ImportError: pandas"
Install: `pip install pandas openpyxl`

### Web server won't start
Check port 5001 availability, kill existing process

### Database locked
Close other connections to imei_orders.db

---

## Project History & Context

### Initial Development (Nov 12-13, 2025)
- Basic API client implementation
- CLI tool created
- Initial batch processing

### Order History Integration (Nov 13-14, 2025)
- Added SQLite database
- Built web interface
- Implemented auto-sync

### Production System (Nov 14, 2025)
- Enterprise batch processing (96x speedup)
- Atomic transactions
- Crash recovery
- Cost safeguards

### Current Focus
- Partnership research (T-Mobile, SCal Mobile)
- Multi-carrier support planning
- Performance optimization for 20K+ daily volume

---

## Key Success Metrics

### Performance
- ✅ Process 20,000 IMEIs in 25 seconds
- ✅ Zero data loss with atomic transactions
- ✅ 95%+ reduction in API calls via caching

### Reliability
- ✅ Automatic retry on failures
- ✅ Crash recovery with checkpoints
- ✅ Duplicate prevention

### Usability
- ✅ Web interface for non-technical users
- ✅ CLI for automation
- ✅ Comprehensive documentation

---

## Contact & Support

### GSM Fusion API
- Website: hammerfusion.com
- Documentation: GSM_Fusion_API.pdf

### This Project
- All documentation in /HAMMER-API/*.md files
- Start with: START_HERE.md or GETTING_STARTED.md
- Technical details: ARCHITECTURE.txt

---

## Version Info

**Current Version**: 1.0.0 (Production)
**Last Major Update**: 2025-11-14
**Python Version Required**: 3.7+
**Platform**: macOS (tested on Darwin 24.6.0)

---

## Directory Structure

```
HAMMER-API/
├── .env                    # API credentials (not in git)
├── .env.example            # Template
├── gsm_fusion_client.py    # API client
├── web_app.py              # Flask app
├── database.py             # Database layer
├── production_submission_system.py  # Batch processor
├── batch_processor.py      # Original batch processor
├── gsm_cli.py              # CLI tool
├── imei_orders.db          # SQLite database
├── requirements.txt        # Dependencies
├── templates/              # HTML templates
├── static/                 # Static assets
├── examples/               # Example scripts
├── checkpoint_*.json       # Recovery checkpoints
├── *.log                   # Log files
└── *.md                    # Documentation (lots!)
```

---

## Development Tips

### When Adding New Features
1. Check existing documentation first (20+ .md files!)
2. Update database.py if schema changes needed
3. Add API methods to gsm_fusion_client.py
4. Update web_app.py routes if UI changes needed
5. Write tests in test_*.py files
6. Update this CLAUDE.md file!

### When Debugging
1. Check logs: web_app.log, server.log
2. Query database directly: `sqlite3 imei_orders.db`
3. Use LOG_LEVEL=DEBUG for verbose output
4. Test with single IMEI first, then small batch

### When Deploying
1. Verify .env has correct credentials
2. Run validate_integration.py
3. Test with small batch (10-20 IMEIs)
4. Monitor logs during deployment
5. Set up log rotation for production

---

## End of Memory File

This file serves as persistent memory across Claude Code sessions. Update it whenever significant changes are made to architecture, dependencies, or project direction.
