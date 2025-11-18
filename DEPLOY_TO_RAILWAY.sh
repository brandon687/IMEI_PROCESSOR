#!/bin/bash

# Deploy HAMMER-API to Railway with Supabase
# Run this script to push to production

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 DEPLOYING HAMMER-API TO RAILWAY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Install: npm i -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Push code to GitHub (in case there are changes)
echo "📤 Pushing code to GitHub..."
git push origin working-version-restore
echo "✅ Code pushed"
echo ""

# Deploy using Railway web dashboard link
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚠️  MANUAL STEP REQUIRED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Railway CLI requires interactive mode for variables."
echo "Please use Railway Dashboard instead:"
echo ""
echo "1. Go to: https://railway.app/dashboard"
echo "2. Select project: IMEI-PROCESSOR"
echo "3. Click 'Variables' tab"
echo "4. Add these variables:"
echo ""
echo "   SUPABASE_URL = https://opinemzfwtoduewqhqwp.supabase.co"
echo ""
echo "   SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waW5lbXpmd3RvZHVld3FocXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNDMzNzcsImV4cCI6MjA3ODgxOTM3N30.KgsAmfnIvCbK1KNSX6CI-AXbd4F_TXtlZ0yQXzRm9KI"
echo ""
echo "5. Railway will auto-deploy after saving variables"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "OR trigger manual deploy with:"
echo "  git commit --allow-empty -m 'Trigger deploy' && git push"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
