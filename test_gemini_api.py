#!/usr/bin/env python3
"""
Test Gemini API key to verify it's working
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    import google.generativeai as genai
except ImportError:
    print("[ERROR] google-generativeai package not installed")
    print("Install it with: pip install google-generativeai")
    sys.exit(1)

def test_gemini_api():
    """Test Gemini API key"""
    print("=" * 70)
    print("TESTING GEMINI API KEY")
    print("=" * 70)
    print()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Please set GEMINI_API_KEY environment variable")
        return False

    print(f"API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
    print()
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("[OK] API key configured")
    except Exception as e:
        print(f"[FAIL] Failed to configure API key: {e}")
        return False
    
    print()
    
    # Test 1: List available models
    print("Test 1: Listing available models...")
    try:
        models = genai.list_models()
        model_names = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        print(f"[OK] Found {len(model_names)} available models")
        if model_names:
            print(f"  Sample models: {', '.join(model_names[:3])}")
    except Exception as e:
        print(f"[FAIL] Failed to list models: {e}")
        return False
    
    print()
    
    # Test 2: Try to generate content with a simple prompt
    print("Test 2: Testing content generation...")
    try:
        # Try with gemini-2.0-flash (as used in genai_service.py)
        model_name = "gemini-2.0-flash"
        print(f"  Using model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello, Gemini API is working!' in one sentence.")
        
        if response and response.text:
            print(f"[OK] Content generation successful")
            print(f"  Response: {response.text[:100]}...")
        else:
            print("[WARNING] No response text received")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"[FAIL] Content generation failed: {error_msg}")
        
        # Check for specific error types
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            print("  [ERROR TYPE] Invalid API key")
            return False
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            print("  [ERROR TYPE] Quota/limit exceeded")
            print()
            print("  NOTE: The API key is VALID, but the free tier quota has been exhausted.")
            print("  Solutions:")
            print("    1. Wait for the quota to reset (usually daily/monthly)")
            print("    2. Upgrade to a paid plan at: https://ai.google.dev/pricing")
            print("    3. Check usage at: https://ai.dev/usage?tab=rate-limit")
            # Since the key is valid, we'll return True but with a warning
            print()
            print("=" * 70)
            print("[WARNING] API key is VALID but quota exceeded")
            print("=" * 70)
            return True  # Key is valid, just quota issue
        elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
            print("  [ERROR TYPE] Permission denied")
            return False
        else:
            print("  [ERROR TYPE] Unknown error")
            return False
    
    print()
    
    # Test 3: Try with the model from genai_service
    print("Test 3: Testing with configured model from genai_service...")
    try:
        from app.services.genai_service import model as configured_model
        response = configured_model.generate_content("Respond with just 'OK' if you can read this.")
        
        if response and response.text:
            print(f"[OK] Configured model works")
            print(f"  Response: {response.text.strip()}")
        else:
            print("[WARNING] Configured model returned no response")
            
    except Exception as e:
        print(f"[WARNING] Could not test configured model: {e}")
        print("  (This is okay if the model name differs)")
    
    print()
    print("=" * 70)
    print("[SUCCESS] Gemini API key is working!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_gemini_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

