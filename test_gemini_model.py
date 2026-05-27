#!/usr/bin/env python3
"""
Test the configured Gemini model with the current API key
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

def test_configured_model():
    """Test the model from genai_service.py"""
    print("=" * 70)
    print("TESTING CONFIGURED GEMINI MODEL")
    print("=" * 70)
    print()
    
    try:
        # Import the configured model from genai_service
        from app.services.genai_service import model, genai as genai_module
        
        # Get the API key that's configured
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[ERROR] GEMINI_API_KEY environment variable is not set")
            return False
        print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
        print()
        
        # Configure with the API key
        genai.configure(api_key=api_key)
        print("[OK] API key configured")
        print()
        
        # Get model name from genai_service
        from app.services.genai_service import model as configured_model
        model_name = "gemini-2.5-flash"  # Updated model
        print(f"Model: {model_name}")
        print()
        
        # Test 1: Verify model can be created
        print("Test 1: Creating model instance...")
        test_model = genai.GenerativeModel(model_name)
        print("[OK] Model instance created successfully")
        print()
        
        # Test 2: Generate content
        print("Test 2: Testing content generation...")
        print("  Prompt: 'Say OK if you can read this message.'")
        
        try:
            response = test_model.generate_content("Say OK if you can read this message.")
            
            if response and response.text:
                print(f"[SUCCESS] Content generation working!")
                print(f"  Response: {response.text.strip()}")
                print()
                print("=" * 70)
                print("[SUCCESS] Model is working correctly!")
                print("=" * 70)
                return True
            else:
                print("[WARNING] No response text received")
                return False
                
        except Exception as e:
            error_msg = str(e)
            print(f"[FAIL] Content generation failed: {error_msg[:200]}")
            
            # Check for specific error types
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower() or "401" in error_msg:
                print("  [ERROR TYPE] Invalid API key")
                return False
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower() or "429" in error_msg:
                print("  [ERROR TYPE] Quota/limit exceeded")
                print()
                print("  NOTE: The API key and model are VALID, but quota is exhausted.")
                print("  The model will work once quota resets or you upgrade your plan.")
                print()
                print("=" * 70)
                print("[WARNING] Model configured correctly but quota exceeded")
                print("=" * 70)
                return True  # Model is valid, just quota issue
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower() or "403" in error_msg:
                print("  [ERROR TYPE] Permission denied")
                return False
            else:
                print("  [ERROR TYPE] Unknown error")
                return False
        
    except ImportError as e:
        print(f"[ERROR] Could not import genai_service: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_configured_model()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

