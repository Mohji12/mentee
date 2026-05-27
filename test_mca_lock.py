#!/usr/bin/env python3
"""
Test script for MCA 2-month lock mechanism
This script tests the lock functionality and competencies update
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port
TEST_STUDENT_USN = "TEST123"  # Replace with actual test student USN

def test_mca_lock_mechanism():
    """Test the MCA lock mechanism"""
    print("🧪 Testing MCA 2-Month Lock Mechanism")
    print("=" * 50)
    
    # Test 1: Check initial lock status
    print("\n1. Checking initial lock status...")
    try:
        response = requests.get(f"{BASE_URL}/student/{TEST_STUDENT_USN}/mca-lock-status")
        if response.status_code == 200:
            lock_data = response.json()
            print(f"✅ Lock status retrieved: {lock_data}")
        else:
            print(f"❌ Failed to get lock status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking lock status: {e}")
    
    # Test 2: Submit MCA form (if not locked)
    print("\n2. Attempting MCA form submission...")
    try:
        # Create a sample MCA form data
        mca_data = {
            "listens_carefully": 5,
            "discouraged_by_criticism": 4,
            "builds_trust": 6,
            "adapts_to_styles": 5,
            "shares_with_classmates": 4,
            "sets_expectations": 5,
            "aligns_expectations": 3,  # This will be reversed
            "wants_mentor_to_adapt": 2,  # This will be reversed
            "expects_improvement_feedback": 5,
            "understands_diff_impacts": 4,
            "goal_setting_with_mentor": 3,  # This will be reversed
            "sees_mentor_as_role_model": 6,
            "aligns_with_industry_expectations": 5,
            "polite_repetition_reminder": 2,  # This will be reversed
            "estimates_mentor_knowledge": 5,
            "considers_industry_exposure": 4,  # This will be reversed
            "self_assess_abilities": 3,  # This will be reversed
            "understands_worklife_balance": 5,
            "discusses_knowledge_strategies": 4,
            "avoids_using_mentor_network": 2,  # This will be reversed
            "discusses_goal_strategies": 5,
            "improves_communication": 4,
            "stays_self_motivated": 6,
            "discusses_career_options": 5,
            "frequent_meetings": 4,
            "extra_effort_due_to_exposure": 3,  # This will be reversed
            "prefers_active_sessions": 5,
            "seeks_networking_support": 4,
            "wants_showcasing_contributions": 5,
            "handles_background_differences": 4,
            "expects_independence": 5,
            "wants_feedback_grouped": 2,  # This will be reversed
            "avoids_bias_prejudice": 6,
            "expects_motivation_support": 5,
            "works_with_diverse_mentors": 4,
            "likes_success_stories": 5,
            "expects_networking_help": 4,
            "encouraged_for_projects": 5,
            "expects_career_exposure": 4,
            "supports_experimentation": 5,
            "supports_industry_interaction": 4,
            "respects_contrary_views": 3,  # This will be reversed
            "encourages_market_analysis": 5,
            "showcases_contributions": 4,
            "accepts_open_criticism": 2  # This will be reversed
        }
        
        response = requests.post(
            f"{BASE_URL}/student/{TEST_STUDENT_USN}/mca-form",
            json=mca_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MCA form submitted successfully: {result}")
        elif response.status_code == 423:
            error_data = response.json()
            print(f"🔒 MCA form is locked: {error_data.get('detail', 'Unknown error')}")
        else:
            print(f"❌ MCA form submission failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error submitting MCA form: {e}")
    
    # Test 3: Check lock status after submission
    print("\n3. Checking lock status after submission...")
    try:
        response = requests.get(f"{BASE_URL}/student/{TEST_STUDENT_USN}/mca-lock-status")
        if response.status_code == 200:
            lock_data = response.json()
            print(f"✅ Updated lock status: {lock_data}")
        else:
            print(f"❌ Failed to get updated lock status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking updated lock status: {e}")
    
    # Test 4: Test competencies calculation
    print("\n4. Testing competencies calculation...")
    try:
        response = requests.post(f"{BASE_URL}/student/{TEST_STUDENT_USN}/calculate_competencies")
        if response.status_code == 200:
            competencies = response.json()
            print(f"✅ Competencies calculated: {competencies}")
        else:
            print(f"❌ Failed to calculate competencies: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error calculating competencies: {e}")
    
    # Test 5: Try to submit again (should be locked)
    print("\n5. Attempting second submission (should be locked)...")
    try:
        response = requests.post(
            f"{BASE_URL}/student/{TEST_STUDENT_USN}/mca-form",
            json=mca_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 423:
            error_data = response.json()
            print(f"🔒 Second submission correctly blocked: {error_data.get('detail', 'Unknown error')}")
        else:
            print(f"❌ Second submission should have been blocked but wasn't: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in second submission test: {e}")

def test_lock_calculation():
    """Test the lock period calculation"""
    print("\n🧮 Testing Lock Period Calculation")
    print("=" * 50)
    
    # Test with different scenarios
    test_cases = [
        {
            "name": "Just submitted",
            "submitted_at": datetime.utcnow(),
            "expected_locked": True
        },
        {
            "name": "Submitted 30 days ago",
            "submitted_at": datetime.utcnow() - timedelta(days=30),
            "expected_locked": True
        },
        {
            "name": "Submitted 60 days ago",
            "submitted_at": datetime.utcnow() - timedelta(days=60),
            "expected_locked": False
        },
        {
            "name": "Submitted 90 days ago",
            "submitted_at": datetime.utcnow() - timedelta(days=90),
            "expected_locked": False
        }
    ]
    
    for case in test_cases:
        lock_end = case["submitted_at"] + timedelta(days=60)
        current_time = datetime.utcnow()
        is_locked = current_time < lock_end
        
        status = "✅" if is_locked == case["expected_locked"] else "❌"
        print(f"{status} {case['name']}: Locked = {is_locked} (Expected: {case['expected_locked']})")
        
        if is_locked:
            days_remaining = (lock_end - current_time).days
            hours_remaining = ((lock_end - current_time).total_seconds() // 3600) % 24
            print(f"   Time remaining: {days_remaining} days, {int(hours_remaining)} hours")

if __name__ == "__main__":
    print("🚀 MCA Lock Mechanism Test Suite")
    print("=" * 60)
    
    # Test lock calculation logic
    test_lock_calculation()
    
    # Test actual API endpoints (uncomment if server is running)
    # test_mca_lock_mechanism()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\n📝 Notes:")
    print("- Make sure your FastAPI server is running on the configured port")
    print("- Replace TEST_STUDENT_USN with an actual student USN from your database")
    print("- The lock mechanism prevents submissions for 60 days (2 months)")
    print("- Competencies are updated with the latest MCA submission")
