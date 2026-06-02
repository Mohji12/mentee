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
    
    # Get API key from environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] No API key found. Please set GEMINI_API_KEY in .env")
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
        print(f"     Sample models: {', '.join(model_names[:3])}")
    except Exception as e:
        print(f"[FAIL] Failed to list models: {e}")
        return False
    
    print()
    
    # Test 2: Create model instance
    print("Test 2: Creating model instance (gemini-2.5-flash)...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("[OK] Model instance created successfully")
    except Exception as e:
        print(f"[FAIL] Failed to create model: {e}")
        return False
    
    print()
    
    # Test 3: Generate content
    print("Test 3: Testing content generation...")
    print("  Prompt: 'Say OK if you can read this message.'")
    try:
        response = model.generate_content("Say OK if you can read this message.")
        if response and response.text:
            print(f"[OK] Response received: {response.text.strip()}")
        else:
            print("[FAIL] Empty response received")
            return False
    except Exception as e:
        print(f"[FAIL] Failed to generate content: {e}")
        error_str = str(e)
        if "API_KEY_INVALID" in error_str or "invalid" in error_str.lower():
            print("\n[ERROR] Your API key appears to be invalid or expired.")
            print("        Please check your Gemini API key and try again.")
        elif "quota" in error_str.lower() or "limit" in error_str.lower():
            print("\n[ERROR] API quota exceeded. Please check your usage limits.")
        return False
    
    print()
    print("=" * 70)
    print("[SUCCESS] All tests passed! Your Gemini API key is working correctly.")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
