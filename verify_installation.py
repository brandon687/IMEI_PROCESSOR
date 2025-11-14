#!/usr/bin/env python3
"""
Installation Verification Script
=================================
Verifies that the GSM Fusion API Client is properly installed and configured.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro}")
        print("  Error: Python 3.7 or higher required")
        return False


def check_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")

    required = {
        'requests': 'Core HTTP library',
        'urllib3': 'HTTP client',
    }

    optional = {
        'pandas': 'Excel file support',
        'openpyxl': 'Excel file support',
        'tabulate': 'CLI table formatting',
        'tqdm': 'Enhanced progress bars',
    }

    all_ok = True

    # Check required
    for module, description in required.items():
        try:
            __import__(module)
            print(f"  ✓ {module} - {description}")
        except ImportError:
            print(f"  ✗ {module} - {description} (REQUIRED)")
            all_ok = False

    # Check optional
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {module} - {description} (optional)")
        except ImportError:
            print(f"  ⚠ {module} - {description} (optional, not installed)")

    return all_ok


def check_files():
    """Check that all required files exist"""
    print("\nChecking project files...")

    required_files = [
        'gsm_fusion_client.py',
        'gsm_cli.py',
        'batch_processor.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        '.env.example'
    ]

    all_ok = True

    for filename in required_files:
        path = Path(filename)
        if path.exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")
            all_ok = False

    return all_ok


def check_configuration():
    """Check configuration"""
    print("\nChecking configuration...")

    # Check for .env file
    if Path('.env').exists():
        print("  ✓ .env file exists")
    else:
        print("  ⚠ .env file not found (copy .env.example to .env)")

    # Check environment variables
    has_key = os.getenv('GSM_FUSION_API_KEY')
    has_user = os.getenv('GSM_FUSION_USERNAME')

    if has_key:
        print("  ✓ GSM_FUSION_API_KEY is set")
    else:
        print("  ⚠ GSM_FUSION_API_KEY not set")

    if has_user:
        print("  ✓ GSM_FUSION_USERNAME is set")
    else:
        print("  ⚠ GSM_FUSION_USERNAME not set")

    if has_key and has_user:
        return True
    else:
        print("\n  To configure credentials:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env and add your credentials")
        print("  3. Or set environment variables:")
        print("     export GSM_FUSION_API_KEY='your-key'")
        print("     export GSM_FUSION_USERNAME='your-username'")
        return False


def check_client():
    """Try to import and initialize client"""
    print("\nChecking GSM Fusion client...")

    try:
        # Try to import
        from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError
        print("  ✓ Client module imported successfully")

        # Try to initialize (will fail if no credentials, but that's ok)
        try:
            client = GSMFusionClient()
            print("  ✓ Client initialized successfully")
            client.close()
            return True
        except GSMFusionAPIError as e:
            if "API key is required" in str(e) or "Username is required" in str(e):
                print("  ⚠ Client requires configuration (credentials not set)")
                return False
            else:
                print(f"  ✗ Client initialization failed: {e}")
                return False

    except ImportError as e:
        print(f"  ✗ Failed to import client: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False


def main():
    """Run all verification checks"""
    print("="*80)
    print("GSM Fusion API Client - Installation Verification")
    print("="*80)

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Project Files': check_files(),
        'Configuration': check_configuration(),
        'Client Import': check_client(),
    }

    # Summary
    print("\n" + "="*80)
    print("Verification Summary")
    print("="*80)

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check:.<40} {status}")

    all_passed = all(results.values())

    print("\n" + "="*80)
    if all_passed:
        print("✓ All checks passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Configure credentials in .env file")
        print("2. Run: python test_client.py")
        print("3. Try: python gsm_cli.py services")
        print("4. See QUICKSTART.md for examples")
    else:
        print("⚠ Some checks failed. Please review the issues above.")
        print("\nTo fix:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure credentials: cp .env.example .env")
        print("3. Run this script again to verify")
    print("="*80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
