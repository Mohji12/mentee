"""Quick check: backend API, login, Cloudinary, Gemini."""
import json
import os
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = "http://127.0.0.1:8000"


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=8) as r:
        return r.status, r.read().decode()


def post(path, payload):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.status, json.loads(r.read().decode())


def main():
    print("=== Backend API (127.0.0.1:8000) ===")
    for path in ["/health", "/"]:
        try:
            status, body = get(path)
            print(f"GET {path}: {status} {body[:100]}")
        except Exception as exc:
            print(f"GET {path}: FAILED - {exc}")

    print("\n=== Admin login (MENTEEAD01) ===")
    try:
        status, data = post("/auth/login", {"id": "MENTEEAD01", "password": "Admin@12345"})
        has_token = bool(data.get("access_token"))
        print(f"POST /auth/login: {status} role={data.get('role')} id={data.get('id')} token={'yes' if has_token else 'no'}")
    except urllib.error.HTTPError as exc:
        print(f"POST /auth/login: HTTP {exc.code} {exc.read().decode()[:200]}")
    except Exception as exc:
        print(f"POST /auth/login: FAILED - {exc}")

    print("\n=== Environment variables ===")
    for key in [
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
        "GEMINI_API_KEY",
        "DATABASE_URL",
    ]:
        val = os.getenv(key)
        if not val:
            print(f"  {key}: NOT SET")
        elif key == "DATABASE_URL":
            print(f"  {key}: SET")
        else:
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
            print(f"  {key}: SET ({masked})")

    cn = os.getenv("CLOUDINARY_CLOUD_NAME")
    ck = os.getenv("CLOUDINARY_API_KEY")
    cs = os.getenv("CLOUDINARY_API_SECRET")
    print("\n=== Cloudinary ===")
    if cn and ck and cs:
        try:
            import cloudinary
            import cloudinary.api

            cloudinary.config(cloud_name=cn, api_key=ck, api_secret=cs, secure=True)
            print("  ping:", cloudinary.api.ping())
        except Exception as exc:
            print(f"  FAILED: {exc}")
    else:
        print("  skipped (missing CLOUDINARY_* in .env)")

    gk = os.getenv("GEMINI_API_KEY")
    print("\n=== Gemini ===")
    if gk:
        try:
            import google.generativeai as genai

            genai.configure(api_key=gk)
            count = sum(1 for _ in genai.list_models())
            print(f"  OK ({count} models)")
        except Exception as exc:
            print(f"  FAILED: {exc}")
    else:
        print("  GEMINI_API_KEY not set")

    print("\n=== Production API (optional) ===")
    prod = "https://mentee.krintixsample.site"
    try:
        status, body = get(prod.replace("127.0.0.1:8000", "") + "/health") if False else (None, None)
    except Exception:
        pass
    try:
        with urllib.request.urlopen(f"{prod}/health", timeout=10) as r:
            print(f"GET {prod}/health: {r.status} {r.read().decode()[:80]}")
    except Exception as exc:
        print(f"GET {prod}/health: FAILED - {exc}")


if __name__ == "__main__":
    main()
