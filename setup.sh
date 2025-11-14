#!/bin/bash
# GSM Fusion API Client Setup Script

set -e

echo "=================================="
echo "GSM Fusion API Client Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.7+
required_version="3.7"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7 or higher is required"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Install dependencies
echo "Installing dependencies..."
if pip3 install -r requirements.txt; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠ IMPORTANT: Edit .env file and add your API credentials:"
    echo "  GSM_FUSION_API_KEY=your-api-key"
    echo "  GSM_FUSION_USERNAME=your-username"
    echo "  GSM_FUSION_BASE_URL=http://hammerfusion.com"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Make CLI executable
chmod +x gsm_cli.py
echo "✓ Made gsm_cli.py executable"
echo ""

# Create examples directory if needed
if [ ! -d "examples" ]; then
    mkdir -p examples
    echo "✓ Created examples directory"
fi

# Run tests (optional)
read -p "Run tests to verify setup? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running tests..."
    echo "=================================="
    if python3 test_client.py; then
        echo "✓ All tests passed"
    else
        echo "⚠ Some tests failed (this is OK if you haven't configured credentials yet)"
    fi
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Test connection: python3 test_client.py"
echo "3. List services: python3 gsm_cli.py services"
echo "4. See QUICKSTART.md for more examples"
echo ""
