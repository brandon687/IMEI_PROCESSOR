#!/usr/bin/env python3
"""
Validation Script: Production System Integration
Verifies that the production submission system is properly integrated
"""

import os
import sys
import importlib.util


def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} exists")
        return True
    else:
        print(f"❌ {filepath} not found")
        return False


def check_import(module_name, filepath):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name} can be imported")
        return True
    except Exception as e:
        print(f"❌ {module_name} import failed: {e}")
        return False


def check_web_app_integration():
    """Check if web_app.py has been properly updated"""
    try:
        with open('web_app.py', 'r') as f:
            content = f.read()

        checks = {
            'Import ProductionSubmissionSystem': 'from production_submission_system import ProductionSubmissionSystem',
            'Import SubmissionResult': 'SubmissionResult',
            'Use production system in /submit': 'system = ProductionSubmissionSystem(',
            'Batch size configured': 'batch_size=100',
            'Max workers configured': 'max_workers=30',
            'Retry configured': 'max_retries=3',
            'Checkpointing enabled': 'enable_checkpointing=True',
            'Show performance metrics': 'duration_seconds',
            'Show success rate': 'success_rate()',
        }

        results = {}
        for name, pattern in checks.items():
            if pattern in content:
                print(f"✅ {name}")
                results[name] = True
            else:
                print(f"❌ {name} - not found")
                results[name] = False

        return all(results.values())

    except Exception as e:
        print(f"❌ Error checking web_app.py: {e}")
        return False


def check_production_system_structure():
    """Check if production_submission_system.py has required components"""
    try:
        with open('production_submission_system.py', 'r') as f:
            content = f.read()

        required_components = {
            'SubmissionResult class': 'class SubmissionResult',
            'ProductionSubmissionSystem class': 'class ProductionSubmissionSystem',
            'submit_batch method': 'def submit_batch',
            'Atomic transaction support': 'BEGIN TRANSACTION',
            'Retry logic': 'for attempt in range',
            'Exponential backoff': '2 ** attempt',
            'Checkpointing': 'checkpoint',
            'Batch ID generation': 'batch_id',
            'Error handling': 'except',
            'Logging': 'logger',
        }

        results = {}
        for name, pattern in required_components.items():
            if pattern in content:
                print(f"✅ {name}")
                results[name] = True
            else:
                print(f"⚠️  {name} - not found (may use different implementation)")
                results[name] = False

        return sum(results.values()) >= 8  # At least 8/10 required

    except Exception as e:
        print(f"❌ Error checking production_submission_system.py: {e}")
        return False


def check_database_structure():
    """Check if database.py supports required operations"""
    try:
        with open('database.py', 'r') as f:
            content = f.read()

        required_methods = {
            'insert_order': 'def insert_order',
            'get_recent_orders': 'def get_recent_orders',
            'update_order_status': 'def update_order_status',
            'search_orders_by_status': 'def search_orders_by_status',
        }

        results = {}
        for name, pattern in required_methods.items():
            if pattern in content:
                print(f"✅ {name} method exists")
                results[name] = True
            else:
                print(f"❌ {name} method not found")
                results[name] = False

        return all(results.values())

    except Exception as e:
        print(f"❌ Error checking database.py: {e}")
        return False


def check_environment():
    """Check if required environment variables are set"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('GSM_FUSION_API_KEY')
        api_url = os.getenv('GSM_FUSION_API_URL')

        if api_key:
            print(f"✅ GSM_FUSION_API_KEY is set (length: {len(api_key)})")
        else:
            print("❌ GSM_FUSION_API_KEY not set")

        if api_url:
            print(f"✅ GSM_FUSION_API_URL is set: {api_url}")
        else:
            print("⚠️  GSM_FUSION_API_URL not set (will use default)")

        return bool(api_key)

    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'requests',
        'python-dotenv',
        'openpyxl',
    ]

    results = {}
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} installed")
            results[package] = True
        except ImportError:
            print(f"❌ {package} not installed")
            results[package] = False

    return all(results.values())


def estimate_performance():
    """Estimate expected performance improvements"""
    print("\n" + "="*80)
    print("PERFORMANCE ESTIMATES")
    print("="*80)

    volumes = [100, 1000, 6000, 20000]

    print("\n| Volume | Before (Individual) | After (Batch) | Speedup |")
    print("|--------|---------------------|---------------|---------|")

    for volume in volumes:
        # Before: Individual API calls (15 sec each, 30 workers)
        before_time = (volume / 30) * 15
        before_min = before_time / 60

        # After: Batch API calls (3.5 sec per 100 IMEIs, 30 workers)
        batches = (volume + 99) // 100
        after_time = (batches / 30) * 3.5
        after_sec = after_time

        speedup = before_time / after_time if after_time > 0 else 0

        print(f"| {volume:,} | {before_min:.1f} min | {after_sec:.1f} sec | {speedup:.0f}x |")

    print("\n" + "="*80)


def main():
    """Run all validation checks"""
    print("="*80)
    print("PRODUCTION SYSTEM INTEGRATION VALIDATION")
    print("="*80)

    all_checks_passed = True

    print("\n1. CHECKING FILES")
    print("-" * 80)
    files = [
        'web_app.py',
        'production_submission_system.py',
        'database.py',
        'gsm_fusion_client.py',
        '.env',
    ]
    for f in files:
        if not check_file_exists(f):
            all_checks_passed = False

    print("\n2. CHECKING DEPENDENCIES")
    print("-" * 80)
    if not check_dependencies():
        all_checks_passed = False
        print("\n⚠️  Install missing packages with:")
        print("   pip install flask requests python-dotenv openpyxl")

    print("\n3. CHECKING ENVIRONMENT")
    print("-" * 80)
    if not check_environment():
        all_checks_passed = False
        print("\n⚠️  Set API key in .env file:")
        print("   GSM_FUSION_API_KEY=your_api_key_here")

    print("\n4. CHECKING WEB APP INTEGRATION")
    print("-" * 80)
    if not check_web_app_integration():
        all_checks_passed = False

    print("\n5. CHECKING PRODUCTION SYSTEM")
    print("-" * 80)
    if not check_production_system_structure():
        all_checks_passed = False

    print("\n6. CHECKING DATABASE")
    print("-" * 80)
    if not check_database_structure():
        all_checks_passed = False

    # Performance estimates
    estimate_performance()

    # Final summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nYour production system is properly integrated and ready to use.")
        print("\nNext steps:")
        print("1. Start the web server: python3 web_app.py")
        print("2. Test with 4 IMEIs via /submit")
        print("3. Test with 100 IMEIs via /batch")
        print("4. Monitor logs: tail -f /tmp/production_submission.log")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the production system.")
        print("\nRefer to PRODUCTION_INTEGRATION.md for detailed setup instructions.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
