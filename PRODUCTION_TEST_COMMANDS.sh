#!/bin/bash
# HAMMER-API Production Testing - Quick Reference Commands
# Production URL: https://web-production-f9a0.up.railway.app

PROD_URL="https://web-production-f9a0.up.railway.app"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     HAMMER-API Production Testing - Quick Commands           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Basic Health Checks
echo "━━━ BASIC HEALTH CHECKS ━━━"
echo ""

echo "1. Health Check:"
echo "   curl $PROD_URL/health | jq"
curl -s $PROD_URL/health | python3 -m json.tool
echo ""

echo "2. API Status (detailed):"
echo "   curl $PROD_URL/api/status | jq"
curl -s $PROD_URL/api/status | python3 -m json.tool
echo ""

# Performance Testing
echo "━━━ PERFORMANCE TESTS ━━━"
echo ""

echo "3. Home Page Performance:"
echo "   curl -w 'Time: %{time_total}s | Status: %{http_code}\n' -o /dev/null -s $PROD_URL/"
curl -w "Time: %{time_total}s | Status: %{http_code}\n" -o /dev/null -s $PROD_URL/
echo ""

echo "4. Services Page Performance:"
echo "   curl -w 'Time: %{time_total}s | Status: %{http_code}\n' -o /dev/null -s $PROD_URL/services"
curl -w "Time: %{time_total}s | Status: %{http_code}\n" -o /dev/null -s $PROD_URL/services
echo ""

# Service Information
echo "━━━ SERVICE INFORMATION ━━━"
echo ""

echo "5. Check Services Count:"
echo "   curl -s $PROD_URL/api/status | jq '.services.gsm_fusion'"
curl -s $PROD_URL/api/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['services']['gsm_fusion'], indent=2))"
echo ""

echo "6. Database Status:"
echo "   curl -s $PROD_URL/api/status | jq '.services.database'"
curl -s $PROD_URL/api/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['services']['database'], indent=2))"
echo ""

# Error Testing
echo "━━━ ERROR HANDLING TESTS ━━━"
echo ""

echo "7. Test 404 Error:"
echo "   curl -w 'Status: %{http_code}\n' -o /dev/null -s $PROD_URL/nonexistent"
curl -w "Status: %{http_code}\n" -o /dev/null -s $PROD_URL/nonexistent
echo ""

echo "8. Test 405 Error (wrong method):"
echo "   curl -X POST -w 'Status: %{http_code}\n' -o /dev/null -s $PROD_URL/"
curl -X POST -w "Status: %{http_code}\n" -o /dev/null -s $PROD_URL/
echo ""

# Advanced Testing
echo "━━━ ADVANCED TESTS ━━━"
echo ""

echo "9. Concurrent Requests Test (3 simultaneous):"
echo "   time (curl -s $PROD_URL/api/status & curl -s $PROD_URL/health & curl -s $PROD_URL/ > /dev/null & wait)"
time (curl -s $PROD_URL/api/status > /dev/null & curl -s $PROD_URL/health > /dev/null & curl -s $PROD_URL/ > /dev/null & wait) 2>&1 | grep real
echo ""

echo "10. Cache Age Check:"
echo "    curl -s $PROD_URL/api/status | jq '.services.cache.message'"
curl -s $PROD_URL/api/status | python3 -c "import sys, json; data=json.load(sys.stdin); print('Cache:', data['services']['cache']['message'])"
echo ""

# Monitoring Commands
echo "━━━ CONTINUOUS MONITORING ━━━"
echo ""

echo "11. Watch health status (refresh every 10s):"
echo "    watch -n 10 'curl -s $PROD_URL/health | jq'"
echo ""

echo "12. Monitor response times:"
echo "    while true; do curl -w 'Time: %{time_total}s\n' -o /dev/null -s $PROD_URL/; sleep 5; done"
echo ""

# Quick Diagnostics
echo "━━━ QUICK DIAGNOSTICS ━━━"
echo ""

echo "13. Full System Status:"
curl -s $PROD_URL/api/status | python3 << 'PYEOF'
import json, sys
data = json.load(sys.stdin)
print("\n┌─────────────────────────────────────────────┐")
print("│         SYSTEM STATUS SNAPSHOT              │")
print("├─────────────────────────────────────────────┤")
print(f"│ Overall: {data['overall']:30s} │")
print(f"│ GSM Fusion: {data['services']['gsm_fusion']['status']:27s} │")
print(f"│ Database: {data['services']['database']['status']:29s} │")
print(f"│ Cache: {data['services']['cache']['status']:32s} │")
print(f"│ Services: {data['services']['gsm_fusion']['message']:28s} │")
print(f"│ Response Time: {data['services']['gsm_fusion']['response_time']} ms{' ' * 22} │")
print("└─────────────────────────────────────────────┘")
PYEOF
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing complete! For detailed report, see:"
echo "  /Users/brandonin/Desktop/HAMMER-API/PRODUCTION_TEST_REPORT.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
