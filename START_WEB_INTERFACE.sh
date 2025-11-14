#!/bin/bash

# GSM Fusion Web Interface Launcher
# Quick start script for the web interface

echo "================================================================================"
echo "🌐 GSM FUSION WEB INTERFACE"
echo "================================================================================"
echo ""
echo "Starting web server..."
echo ""

cd "$(dirname "$0")"

python3 web_app.py
