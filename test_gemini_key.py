"""Quick test for Gemini API (uses app.services.genai_service). Run: python test_gemini_key.py"""
import sys

def main():
    print("Testing Gemini API (using app genai_service config)...")
    try:
        from app.services.genai_service import model
        response = model.generate_content("Reply with exactly: OK")
        text = (response.text or "").strip()
        print("Response:", text[:200] if text else "(empty)")
        print("\n[SUCCESS] Gemini API key is working.")
        return 0
    except ImportError as e:
        print("ERROR: pip install google-generativeai")
        return 1
    except Exception as e:
        print(f"\n[FAILED] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
