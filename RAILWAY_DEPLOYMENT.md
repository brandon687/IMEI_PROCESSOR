# Railway Deployment Guide

## Overview

This guide covers deploying HAMMER-API to Railway.app for production use.

## Prerequisites

- GitHub account with access to https://github.com/brandon687/IMEI_PROCESSOR.git
- Railway account (sign up at https://railway.app)
- GSM Fusion API credentials

## Deployment Steps

### 1. Connect to Railway

1. Visit https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `brandon687/IMEI_PROCESSOR`

### 2. Configure Environment Variables

In Railway dashboard, go to your project settings and add these variables:

**Required:**
```
GSM_FUSION_API_KEY=your-api-key-here
GSM_FUSION_USERNAME=your-username-here
GSM_FUSION_BASE_URL=http://hammerfusion.com
```

**Optional (with defaults):**
```
LOG_LEVEL=INFO
AUTO_SYNC_INTERVAL=300
PORT=5000
```

**Important:** Never commit these values to GitHub. Railway securely manages environment variables.

### 3. Verify Configuration Files

Railway will automatically detect these files (already included):

- `railway.json` - Railway-specific configuration
- `Procfile` - Defines the web server command
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Python dependencies

### 4. Deploy

Railway will automatically:
1. Install Python 3.11
2. Install dependencies from `requirements.txt`
3. Start the web server using `gunicorn`
4. Assign a public URL (e.g., `your-app.up.railway.app`)

### 5. Access Your Application

Once deployed, Railway provides a public URL. Your app will be available at:
```
https://your-project-name.up.railway.app
```

## Database Considerations

### SQLite in Production

The default SQLite database (`imei_orders.db`) works fine for Railway deployments with caveats:

**Pros:**
- Zero configuration
- Fast for small-medium loads
- Works immediately

**Cons:**
- Database resets on container restarts
- No persistence across deployments
- Not suitable for critical data long-term

### Recommended: Railway PostgreSQL

For production with persistent data:

1. In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
2. Railway auto-provisions a PostgreSQL instance
3. Update `database.py` to use PostgreSQL instead of SQLite
4. Add `psycopg2-binary` to `requirements.txt`

**Migration code example:**
```python
import os
import psycopg2

# Use DATABASE_URL provided by Railway
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL)
else:
    # Fallback to SQLite for local dev
    conn = sqlite3.connect('imei_orders.db')
```

## Scaling Configuration

### Current Setup
- 2 gunicorn workers (handles ~100 concurrent requests)
- 120-second timeout (allows long-running batch jobs)
- Auto-restart on failure (up to 10 retries)

### Adjusting Workers

Edit `railway.json` to change worker count:
```json
{
  "deploy": {
    "startCommand": "gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120"
  }
}
```

**Rule of thumb:** `workers = (2 x CPU cores) + 1`

## Monitoring

### Logs

View real-time logs in Railway dashboard:
1. Click your project
2. Select "Deployments"
3. Click latest deployment
4. View logs tab

### Health Checks

Railway automatically monitors your app:
- HTTP health checks on root path (`/`)
- Auto-restarts on failures
- Email notifications on crashes

## Cost Estimates

### Railway Pricing (as of 2025)
- **Hobby Plan:** $5/month + usage
  - 500 hours included
  - $0.000231/GB-hour for RAM
  - $0.000463/vCPU-hour

- **Pro Plan:** $20/month + usage
  - Better performance
  - Priority support
  - More included hours

### Typical Usage (HAMMER-API)
- **Light:** <1,000 orders/day → ~$5-10/month
- **Medium:** 5,000-10,000 orders/day → ~$15-30/month
- **Heavy:** 20,000+ orders/day → ~$50-100/month

**Note:** Most cost is GSM Fusion API credits, not hosting.

## Security Best Practices

### Environment Variables
- ✅ Store API keys in Railway environment variables
- ✅ Never commit `.env` to GitHub
- ✅ Rotate API keys regularly
- ✅ Use Railway's secret management

### Network Security
- Railway provides HTTPS by default
- DDoS protection included
- Automatic security patches

### Application Security
- Set `LOG_LEVEL=WARNING` in production (less verbose)
- Enable rate limiting if needed
- Monitor for suspicious activity

## Troubleshooting

### Deployment Fails

**Check build logs:**
1. Railway dashboard → Deployments → Failed deployment
2. Look for Python errors or missing dependencies

**Common issues:**
- Missing dependency in `requirements.txt`
- Python version mismatch (update `runtime.txt`)
- Syntax errors in code

### App Crashes on Start

**Check environment variables:**
1. Verify `GSM_FUSION_API_KEY` is set
2. Verify `GSM_FUSION_USERNAME` is set
3. Check logs for "KeyError" or "missing required"

### Database Issues

**SQLite limitations:**
- If data disappears after restart, database file was lost
- Solution: Migrate to PostgreSQL (see above)

**Connection errors:**
- Check Railway service logs
- Verify DATABASE_URL if using PostgreSQL

### Slow Performance

**Increase workers:**
```json
"startCommand": "gunicorn web_app:app --workers 4"
```

**Upgrade Railway plan:**
- Hobby → Pro for more resources
- Check CPU/RAM usage in metrics

## Continuous Deployment

### Automatic Deploys

Railway auto-deploys on GitHub push:
1. Push code to `main` branch
2. Railway detects change
3. Rebuilds and deploys automatically
4. Zero downtime deployments

### Manual Deploys

Force redeploy in Railway dashboard:
1. Go to Deployments
2. Click "Deploy" → "Redeploy"

## Rollback

If deployment breaks:
1. Railway dashboard → Deployments
2. Find last working deployment
3. Click "..." → "Redeploy"

## Custom Domain

### Add Your Domain

1. Railway dashboard → Settings → Domains
2. Click "Add Domain"
3. Enter your domain (e.g., `imei.yourdomain.com`)
4. Add CNAME record to DNS:
   ```
   CNAME imei.yourdomain.com → your-app.up.railway.app
   ```
5. Railway auto-provisions SSL certificate

## Environment-Specific Configuration

### Development vs Production

Use environment variables to toggle features:

```python
import os

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
AUTO_SYNC = os.environ.get('AUTO_SYNC_INTERVAL', '300')
```

**In Railway:**
```
DEBUG=False
AUTO_SYNC_INTERVAL=300
```

**Locally:**
```
DEBUG=True
AUTO_SYNC_INTERVAL=60
```

## Backup Strategy

### Database Backups

**SQLite (manual):**
1. Download database file via Railway CLI
2. Store securely off-site

**PostgreSQL (automatic):**
- Railway provides daily backups
- Point-in-time recovery available
- 7-day retention on Pro plan

### Code Backups

- Code is safe in GitHub
- Tag releases: `git tag v1.0.0 && git push --tags`
- Railway stores deployment history

## Performance Optimization

### Caching

Add Redis for session caching:
1. Railway → New → Database → Redis
2. Update code to use Redis for sessions
3. Reduces database load

### CDN

For static assets:
1. Upload to Railway's static file hosting
2. Or use external CDN (Cloudflare, etc.)

## Support

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Email: team@railway.app

### HAMMER-API Issues
- GitHub: https://github.com/brandon687/IMEI_PROCESSOR/issues
- Check existing documentation in repo

## Quick Reference

### Common Commands (Railway CLI)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run command in production
railway run python gsm_cli.py services

# Set environment variable
railway variables set GSM_FUSION_API_KEY=xxx

# Download database
railway run cat imei_orders.db > backup.db
```

## Next Steps

After deployment:
1. Test order submission via web UI
2. Verify database persistence
3. Set up monitoring/alerts
4. Configure custom domain (optional)
5. Enable PostgreSQL for production data (recommended)

## Summary

Railway deployment is:
- ✅ **Fast** - Deploy in minutes
- ✅ **Easy** - Zero DevOps configuration
- ✅ **Scalable** - Grows with your needs
- ✅ **Affordable** - Pay-as-you-go pricing
- ✅ **Reliable** - Auto-restarts and monitoring

Your app is now live at: https://your-project.up.railway.app
