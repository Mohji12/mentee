from typing import Any
from pydantic import BaseModel, Field

class MentoringAssessment(BaseModel):
    # Page 1 (8 questions)
    listens_carefully: Any
    discouraged_by_criticism: Any
    builds_trust: Any
    adapts_to_styles: Any
    shares_with_classmates: Any
    sets_expectations: Any
    aligns_expectations: Any
    wants_mentor_to_adapt: Any
    
    # Page 2 (8 questions)
    expects_improvement_feedback: Any
    understands_diff_impacts: Any
    goal_setting_with_mentor: Any
    sees_mentor_as_role_model: Any
    aligns_with_industry_expectations: Any
    polite_repetition_reminder: Any
    estimates_mentor_knowledge: Any
    considers_industry_exposure: Any
    
    # Page 3 (8 questions)
    self_assess_abilities: Any
    understands_worklife_balance: Any
    discusses_knowledge_strategies: Any
    avoids_using_mentor_network: Any
    discusses_goal_strategies: Any
    improves_communication: Any
    stays_self_motivated: Any
    discusses_career_options: Any
    
    # Page 4 (8 questions)
    frequent_meetings: Any
    extra_effort_due_to_exposure: Any
    prefers_active_sessions: Any
    seeks_networking_support: Any
    wants_showcasing_contributions: Any
    handles_background_differences: Any
    expects_independence: Any
    wants_feedback_grouped: Any
    
    # Page 5 (8 questions)
    avoids_bias_prejudice: Any
    expects_motivation_support: Any
    works_with_diverse_mentors: Any
    likes_success_stories: Any
    expects_networking_help: Any
    encouraged_for_projects: Any
    expects_career_exposure: Any
    supports_experimentation: Any
    
    # Page 6 (5 questions)
    supports_industry_interaction: Any
    respects_contrary_views: Any
    encourages_market_analysis: Any
    showcases_contributions: Any
    accepts_open_criticism: Any

    class Config:
        populate_by_name = True
        str_strip_whitespace = True
