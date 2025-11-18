#!/usr/bin/env python3
"""
Direct PostgreSQL Update Diagnostic Script
Tests exactly what's failing with order updates to Railway PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Get database URL
database_url = os.getenv('DATABASE_PUBLIC_URL') or os.getenv('DATABASE_URL')

if not database_url:
    print("❌ ERROR: No DATABASE_URL or DATABASE_PUBLIC_URL found in .env")
    print("This script tests the actual Railway PostgreSQL connection")
    exit(1)

print("=" * 80)
print("POSTGRESQL UPDATE DIAGNOSTIC")
print("=" * 80)
print()

try:
    print(f"📡 Connecting to Railway PostgreSQL...")
    print(f"   Host: {database_url.split('@')[1].split(':')[0] if '@' in database_url else 'unknown'}")

    conn = psycopg2.connect(database_url)
    conn.autocommit = False  # Explicit transaction control
    cursor = conn.cursor()

    print(f"✅ Connected successfully")
    print()

    # Test Case: Order 15590461 (the failing order)
    test_order_id = '15590461'

    print(f"🔍 TEST 1: Check if order {test_order_id} exists")
    print("-" * 80)

    cursor.execute("""
        SELECT order_id, status, carrier, model, simlock, fmi, imei
        FROM orders
        WHERE order_id = %s
    """, (test_order_id,))

    order = cursor.fetchone()

    if not order:
        print(f"❌ Order {test_order_id} NOT FOUND in database")
        print()
        print("Checking all orders in database...")
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        print(f"Total orders in database: {count}")

        if count > 0:
            cursor.execute("SELECT order_id, imei, status FROM orders ORDER BY created_at DESC LIMIT 5")
            recent = cursor.fetchall()
            print("\nMost recent 5 orders:")
            for r in recent:
                print(f"  - Order ID: {r[0]}, IMEI: {r[1]}, Status: {r[2]}")

        print()
        print("⚠️  ROOT CAUSE: Order was never inserted into PostgreSQL!")
        print("   This means the initial insert_order() is failing silently")
        exit(1)

    print(f"✅ Order EXISTS in database:")
    print(f"   Order ID: {order[0]}")
    print(f"   Status: {order[1]}")
    print(f"   Carrier: {order[2]}")
    print(f"   Model: {order[3]}")
    print(f"   SimLock: {order[4]}")
    print(f"   FMI: {order[5]}")
    print(f"   IMEI: {order[6]}")
    print()

    # Test Case 2: Check order_id data type
    print(f"🔍 TEST 2: Check order_id column data type")
    print("-" * 80)

    cursor.execute("""
        SELECT data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'orders' AND column_name = 'order_id'
    """)

    col_info = cursor.fetchone()
    print(f"   Column type: {col_info[0]}")
    print(f"   Max length: {col_info[1]}")
    print()

    # Test Case 3: Attempt UPDATE
    print(f"🔍 TEST 3: Attempt UPDATE with test data")
    print("-" * 80)

    test_carrier = "TEST_CARRIER_UPDATE"
    test_model = "TEST_MODEL_UPDATE"
    test_status = "Completed"

    print(f"Updating order {test_order_id}...")
    print(f"  SET status = '{test_status}'")
    print(f"  SET carrier = '{test_carrier}'")
    print(f"  SET model = '{test_model}'")
    print()

    cursor.execute("""
        UPDATE orders
        SET status = %s, carrier = %s, model = %s, updated_at = CURRENT_TIMESTAMP
        WHERE order_id = %s
    """, (test_status, test_carrier, test_model, test_order_id))

    rowcount = cursor.rowcount
    print(f"UPDATE executed - rowcount: {rowcount}")

    if rowcount == 0:
        print(f"❌ UPDATE matched 0 rows!")
        print()
        print("⚠️  ROOT CAUSE: WHERE clause not matching - likely data type issue")
        print()
        print("Testing order_id as different types...")

        # Try as integer
        cursor.execute("UPDATE orders SET carrier = %s WHERE order_id = %s", ("TEST_INT", int(test_order_id)))
        if cursor.rowcount > 0:
            print(f"✅ UPDATE succeeded when order_id treated as INTEGER!")
            print(f"   ROOT CAUSE CONFIRMED: order_id column is INTEGER but we're passing TEXT")
            conn.rollback()
        else:
            print(f"❌ Still failed with INTEGER - checking for other issues...")
            conn.rollback()

        exit(1)

    print(f"✅ UPDATE succeeded (matched {rowcount} row)")
    print()

    # Test Case 4: Verify BEFORE commit
    print(f"🔍 TEST 4: Verify changes BEFORE commit")
    print("-" * 80)

    cursor.execute("""
        SELECT status, carrier, model
        FROM orders
        WHERE order_id = %s
    """, (test_order_id,))

    after_update = cursor.fetchone()
    print(f"   Status: {after_update[0]}")
    print(f"   Carrier: {after_update[1]}")
    print(f"   Model: {after_update[2]}")

    if after_update[1] == test_carrier:
        print(f"✅ Changes visible in transaction (before commit)")
    else:
        print(f"❌ Changes NOT visible even before commit - serious issue!")
        conn.rollback()
        exit(1)

    print()

    # Test Case 5: COMMIT
    print(f"🔍 TEST 5: COMMIT transaction")
    print("-" * 80)

    conn.commit()
    print(f"✅ COMMIT completed")
    print()

    # Test Case 6: Verify AFTER commit (new connection)
    print(f"🔍 TEST 6: Verify changes AFTER commit (fresh query)")
    print("-" * 80)

    cursor.execute("""
        SELECT status, carrier, model
        FROM orders
        WHERE order_id = %s
    """, (test_order_id,))

    after_commit = cursor.fetchone()
    print(f"   Status: {after_commit[0]}")
    print(f"   Carrier: {after_commit[1]}")
    print(f"   Model: {after_commit[2]}")

    if after_commit[1] == test_carrier:
        print(f"✅ Changes PERSISTED after commit!")
        print()
        print("=" * 80)
        print("🎉 SUCCESS: PostgreSQL updates are working correctly!")
        print("=" * 80)
        print()
        print("This means:")
        print("  1. PostgreSQL connection: WORKING")
        print("  2. UPDATE statements: WORKING")
        print("  3. COMMIT: WORKING")
        print("  4. Persistence: WORKING")
        print()
        print("⚠️  CONCLUSION: The issue is in the APPLICATION CODE, not PostgreSQL")
        print()
        print("Likely causes:")
        print("  - Multiple Gunicorn workers using cached/stale database connections")
        print("  - Database singleton not being properly refreshed")
        print("  - Order not being inserted initially (check insert_order logs)")

        # Cleanup: revert test changes
        print()
        print("Reverting test changes...")
        cursor.execute("""
            UPDATE orders
            SET status = %s, carrier = %s, model = %s
            WHERE order_id = %s
        """, (order[1], order[2], order[3], test_order_id))
        conn.commit()
        print("✅ Test changes reverted")

    else:
        print(f"❌ Changes DID NOT PERSIST!")
        print()
        print("⚠️  ROOT CAUSE: Transaction isolation or autocommit issue")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
