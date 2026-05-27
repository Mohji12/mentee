#!/usr/bin/env python3
"""
Test script for MCA backend components
Tests Schema, Model, and API alignment
"""

def test_schema_fields():
    """Test that schema has exactly 45 fields"""
    try:
        from app.schemas.mca_assignment import MentoringAssessment
        
        # Get all field names
        field_names = list(MentoringAssessment.__fields__.keys())
        
        print(f"✅ Schema has {len(field_names)} fields")
        print(f"Field names: {field_names}")
        
        # Check for required fields
        required_fields = [
            "listens_carefully", "discouraged_by_criticism", "builds_trust", "adapts_to_styles",
            "shares_with_classmates", "sets_expectations", "aligns_expectations", "wants_mentor_to_adapt",
            "expects_improvement_feedback", "understands_diff_impacts", "goal_setting_with_mentor",
            "sees_mentor_as_role_model", "aligns_with_industry_expectations", "polite_repetition_reminder",
            "estimates_mentor_knowledge", "considers_industry_exposure", "self_assess_abilities",
            "understands_worklife_balance", "discusses_knowledge_strategies", "avoids_using_mentor_network",
            "discusses_goal_strategies", "improves_communication", "stays_self_motivated",
            "discusses_career_options", "frequent_meetings", "extra_effort_due_to_exposure",
            "prefers_active_sessions", "seeks_networking_support", "wants_showcasing_contributions",
            "handles_background_differences", "expects_independence", "wants_feedback_grouped",
            "avoids_bias_prejudice", "expects_motivation_support", "works_with_diverse_mentors",
            "likes_success_stories", "expects_networking_help", "encouraged_for_projects",
            "expects_career_exposure", "supports_experimentation", "supports_industry_interaction",
            "respects_contrary_views", "encourages_market_analysis", "showcases_contributions",
            "accepts_open_criticism"
        ]
        
        missing_fields = [field for field in required_fields if field not in field_names]
        extra_fields = [field for field in field_names if field not in required_fields]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All required fields present")
            
        if extra_fields:
            print(f"❌ Extra fields: {extra_fields}")
        else:
            print("✅ No extra fields")
            
        return len(field_names) == 45 and len(missing_fields) == 0 and len(extra_fields) == 0
        
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False

def test_model_fields():
    """Test that database model has exactly 45 fields"""
    try:
        from app.db.models.MCA_assignments import MentorshipAssessment
        
        # Get all column names (excluding id, student_usn, submitted_at)
        column_names = [column.name for column in MentorshipAssessment.__table__.columns 
                       if column.name not in ['id', 'student_usn', 'submitted_at']]
        
        print(f"✅ Model has {len(column_names)} question fields")
        print(f"Question fields: {column_names}")
        
        # Check for required fields
        required_fields = [
            "listens_carefully", "discouraged_by_criticism", "builds_trust", "adapts_to_styles",
            "shares_with_classmates", "sets_expectations", "aligns_expectations", "wants_mentor_to_adapt",
            "expects_improvement_feedback", "understands_diff_impacts", "goal_setting_with_mentor",
            "sees_mentor_as_role_model", "aligns_with_industry_expectations", "polite_repetition_reminder",
            "estimates_mentor_knowledge", "considers_industry_exposure", "self_assess_abilities",
            "understands_worklife_balance", "discusses_knowledge_strategies", "avoids_using_mentor_network",
            "discusses_goal_strategies", "improves_communication", "stays_self_motivated",
            "discusses_career_options", "frequent_meetings", "extra_effort_due_to_exposure",
            "prefers_active_sessions", "seeks_networking_support", "wants_showcasing_contributions",
            "handles_background_differences", "expects_independence", "wants_feedback_grouped",
            "avoids_bias_prejudice", "expects_motivation_support", "works_with_diverse_mentors",
            "likes_success_stories", "expects_networking_help", "encouraged_for_projects",
            "expects_career_exposure", "supports_experimentation", "supports_industry_interaction",
            "respects_contrary_views", "encourages_market_analysis", "showcases_contributions",
            "accepts_open_criticism"
        ]
        
        missing_fields = [field for field in required_fields if field not in column_names]
        extra_fields = [field for field in column_names if field not in required_fields]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All required fields present")
            
        if extra_fields:
            print(f"❌ Extra fields: {extra_fields}")
        else:
            print("✅ No extra fields")
            
        return len(column_names) == 45 and len(missing_fields) == 0 and len(extra_fields) == 0
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def test_api_questions():
    """Test that API returns exactly 45 questions"""
    try:
        from app.routes.student.mca import get_mca_questions
        
        # Get questions from API
        questions = get_mca_questions()
        
        print(f"✅ API returns {len(questions)} questions")
        
        # Check for required questions
        required_aliases = [
            "listens_carefully", "discouraged_by_criticism", "builds_trust", "adapts_to_styles",
            "shares_with_classmates", "sets_expectations", "aligns_expectations", "wants_mentor_to_adapt",
            "expects_improvement_feedback", "understands_diff_impacts", "goal_setting_with_mentor",
            "sees_mentor_as_role_model", "aligns_with_industry_expectations", "polite_repetition_reminder",
            "estimates_mentor_knowledge", "considers_industry_exposure", "self_assess_abilities",
            "understands_worklife_balance", "discusses_knowledge_strategies", "avoids_using_mentor_network",
            "discusses_goal_strategies", "improves_communication", "stays_self_motivated",
            "discusses_career_options", "frequent_meetings", "extra_effort_due_to_exposure",
            "prefers_active_sessions", "seeks_networking_support", "wants_showcasing_contributions",
            "handles_background_differences", "expects_independence", "wants_feedback_grouped",
            "avoids_bias_prejudice", "expects_motivation_support", "works_with_diverse_mentors",
            "likes_success_stories", "expects_networking_help", "encouraged_for_projects",
            "expects_career_exposure", "supports_experimentation", "supports_industry_interaction",
            "respects_contrary_views", "encourages_market_analysis", "showcases_contributions",
            "accepts_open_criticism"
        ]
        
        question_aliases = [q["alias"] for q in questions]
        
        missing_aliases = [alias for alias in required_aliases if alias not in question_aliases]
        extra_aliases = [alias for alias in question_aliases if alias not in required_aliases]
        
        if missing_aliases:
            print(f"❌ Missing aliases: {missing_aliases}")
        else:
            print("✅ All required aliases present")
            
        if extra_aliases:
            print(f"❌ Extra aliases: {extra_aliases}")
        else:
            print("✅ No extra aliases")
            
        return len(questions) == 45 and len(missing_aliases) == 0 and len(extra_aliases) == 0
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing MCA Backend Components...")
    print("=" * 50)
    
    schema_ok = test_schema_fields()
    print("-" * 50)
    
    model_ok = test_model_fields()
    print("-" * 50)
    
    api_ok = test_api_questions()
    print("-" * 50)
    
    print("📊 Test Results:")
    print(f"Schema: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"Model:  {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"API:    {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if schema_ok and model_ok and api_ok:
        print("\n🎉 All tests passed! Backend is perfectly aligned.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
