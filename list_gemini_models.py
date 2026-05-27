#!/usr/bin/env python3
"""
List all available Gemini models to find free alternatives
"""

import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("Set GEMINI_API_KEY environment variable")

genai.configure(api_key=api_key)

print("=" * 70)
print("AVAILABLE GEMINI MODELS")
print("=" * 70)
print()

try:
    models = genai.list_models()
    
    # Filter models that support generateContent
    generate_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
    
    print(f"Total models with generateContent: {len(generate_models)}")
    print()
    
    # Group by model family
    flash_models = [m for m in generate_models if 'flash' in m.name.lower()]
    pro_models = [m for m in generate_models if 'pro' in m.name.lower()]
    other_models = [m for m in generate_models if 'flash' not in m.name.lower() and 'pro' not in m.name.lower()]
    
    print("FLASH MODELS (Faster, usually better free tier quota):")
    print("-" * 70)
    for model in flash_models:
        print(f"  - {model.name}")
        if model.display_name:
            print(f"    Display: {model.display_name}")
    
    print()
    print("PRO MODELS (More capable, may have stricter quotas):")
    print("-" * 70)
    for model in pro_models:
        print(f"  - {model.name}")
        if model.display_name:
            print(f"    Display: {model.display_name}")
    
    if other_models:
        print()
        print("OTHER MODELS:")
        print("-" * 70)
        for model in other_models:
            print(f"  - {model.name}")
            if model.display_name:
                print(f"    Display: {model.display_name}")
    
    print()
    print("=" * 70)
    print("RECOMMENDED FREE MODELS (usually better quota):")
    print("=" * 70)
    recommended = [m.name for m in flash_models if '1.5' in m.name or '1.0' in m.name]
    if recommended:
        for model_name in recommended:
            print(f"  - {model_name}")
    else:
        print("  - gemini-1.5-flash (if available)")
        print("  - gemini-1.5-pro (if available)")
    
except Exception as e:
    print(f"Error listing models: {e}")

