#!/usr/bin/env python3
"""
Simple script to test database connection
Run this from the project root: python test_db_connection.py
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from app.db.database import engine, SessionLocal

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection...")
    print("=" * 60)
    
    # Get database URL (masked for security)
    from app.db.database import DATABASE_URL
    db_url_parts = DATABASE_URL.split('@')
    if len(db_url_parts) > 1:
        masked_url = f"{db_url_parts[0].split('//')[0]}//***@{db_url_parts[1]}"
    else:
        masked_url = "***"
    print(f"Database URL: {masked_url}")
    print()
    
    # Test 1: Engine connection
    print("Test 1: Testing engine connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("[OK] Engine connection: SUCCESS")
            else:
                print("[FAIL] Engine connection: FAILED (unexpected result)")
                return False
    except Exception as e:
        print(f"[FAIL] Engine connection: FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)}")
        return False
    
    print()
    
    # Test 2: Session connection
    print("Test 2: Testing session connection...")
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT DATABASE() as db_name, VERSION() as version"))
        row = result.fetchone()
        if row:
            print("[OK] Session connection: SUCCESS")
            print(f"  Database Name: {row[0]}")
            print(f"  MySQL Version: {row[1]}")
        else:
            print("[FAIL] Session connection: FAILED (no result)")
            return False
    except (SQLAlchemyError, DisconnectionError) as e:
        print(f"[FAIL] Session connection: FAILED")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")
        return False
    except Exception as e:
        print(f"[FAIL] Session connection: FAILED")
        print(f"  Unexpected Error: {type(e).__name__}: {str(e)}")
        return False
    finally:
        db.close()
    
    print()
    
    # Test 3: Pool status
    print("Test 3: Checking connection pool status...")
    try:
        pool = engine.pool
        print(f"  Pool Size: {pool.size()}")
        print(f"  Checked Out: {pool.checkedout()}")
        print(f"  Overflow: {pool.overflow()}")
        print("[OK] Pool status: OK")
    except Exception as e:
        print(f"[FAIL] Pool status check: FAILED - {str(e)}")
    
    print()
    print("=" * 60)
    print("[OK] All connection tests PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

