from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class MentorshipAssessment(Base):
    __tablename__ = "mentoring_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)

    # Page 1 (8 questions)
    listens_carefully = Column(Integer)
    discouraged_by_criticism = Column(Integer)
    builds_trust = Column(Integer)
    adapts_to_styles = Column(Integer)
    shares_with_classmates = Column(Integer)
    sets_expectations = Column(Integer)
    aligns_expectations = Column(Integer)
    wants_mentor_to_adapt = Column(Integer)
    
    # Page 2 (8 questions)
    expects_improvement_feedback = Column(Integer)
    understands_diff_impacts = Column(Integer)
    goal_setting_with_mentor = Column(Integer)
    sees_mentor_as_role_model = Column(Integer)
    aligns_with_industry_expectations = Column(Integer)
    polite_repetition_reminder = Column(Integer)
    estimates_mentor_knowledge = Column(Integer)
    considers_industry_exposure = Column(Integer)
    
    # Page 3 (8 questions)
    self_assess_abilities = Column(Integer)
    understands_worklife_balance = Column(Integer)
    discusses_knowledge_strategies = Column(Integer)
    avoids_using_mentor_network = Column(Integer)
    discusses_goal_strategies = Column(Integer)
    improves_communication = Column(Integer)
    stays_self_motivated = Column(Integer)
    discusses_career_options = Column(Integer)
    
    # Page 4 (8 questions)
    frequent_meetings = Column(Integer)
    extra_effort_due_to_exposure = Column(Integer)
    prefers_active_sessions = Column(Integer)
    seeks_networking_support = Column(Integer)
    wants_showcasing_contributions = Column(Integer)
    handles_background_differences = Column(Integer)
    expects_independence = Column(Integer)
    wants_feedback_grouped = Column(Integer)
    
    # Page 5 (8 questions)
    avoids_bias_prejudice = Column(Integer)
    expects_motivation_support = Column(Integer)
    works_with_diverse_mentors = Column(Integer)
    likes_success_stories = Column(Integer)
    expects_networking_help = Column(Integer)
    encouraged_for_projects = Column(Integer)
    expects_career_exposure = Column(Integer)
    supports_experimentation = Column(Integer)
    
    # Page 6 (5 questions)
    supports_industry_interaction = Column(Integer)
    respects_contrary_views = Column(Integer)
    encourages_market_analysis = Column(Integer)
    showcases_contributions = Column(Integer)
    accepts_open_criticism = Column(Integer)
    
    # Timestamp
    submitted_at = Column(DateTime, server_default=func.now())
    
    # Add unique constraint to prevent multiple submissions within lock period
    __table_args__ = (
        # This will be handled in application logic for 2-month lock
    ) 