"""
Quick check that the API app loads and key routes exist.
Run from project root: python check_api.py
"""
import sys

def main():
    print("Checking Mentee Tracker API...")
    try:
        from app.main import app
        print("  [OK] app.main loads")
    except Exception as e:
        print(f"  [FAIL] app.main: {e}")
        return 1

    # Test that routes are registered
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    for path in ["/", "/health"]:
        if path in routes:
            print(f"  [OK] Route exists: {path}")
        else:
            print(f"  [WARN] Route not found: {path}")

    # Optional: hit the root route via ASGI test client (no server needed)
    try:
        from starlette.testclient import TestClient
        client = TestClient(app)
        r = client.get("/")
        if r.status_code == 200:
            print(f"  [OK] GET / returns 200: {r.json()}")
        else:
            print(f"  [WARN] GET / returned {r.status_code}")
        r2 = client.get("/health")
        if r2.status_code == 200:
            print(f"  [OK] GET /health returns 200: {r2.json()}")
        else:
            print(f"  [WARN] GET /health returned {r2.status_code}")
    except Exception as e:
        print(f"  [SKIP] TestClient: {e}")

    print("\nAPI check done. To run the server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    return 0

if __name__ == "__main__":
    sys.exit(main())
