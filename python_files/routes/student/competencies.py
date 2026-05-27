from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.competencies import Competencies

router = APIRouter()

@router.post("/calculate_competencies")
def calculate_competencies(usn: str, db: Session = Depends(get_db)):
    # Get the latest MCA assessment (most recent submission)
    assessment = db.query(MentorshipAssessment).filter(
        MentorshipAssessment.student_usn == usn
    ).order_by(MentorshipAssessment.submitted_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No MCA assessment found for this student")

    competency_mapping = {
        "Active_Listening": [
            assessment.listens_carefully,
            assessment.adapts_to_styles,
            assessment.wants_mentor_to_adapt,
            assessment.polite_repetition_reminder,
            assessment.improves_communication
        ],
        "Building_Trust": [
            assessment.builds_trust,
            assessment.aligns_expectations,
            assessment.handles_background_differences,
            assessment.avoids_bias_prejudice,
            assessment.works_with_diverse_mentors
        ],
        "Encouraging": [
            assessment.aligns_with_industry_expectations,
            assessment.stays_self_motivated,
            assessment.seeks_networking_support,
            assessment.wants_showcasing_contributions,
            assessment.expects_independence,
        ],
        "Identifying_Goals_Current_Reality": [
            assessment.sets_expectations,
            assessment.goal_setting_with_mentor,
            assessment.discusses_goal_strategies,
            assessment.expects_career_exposure,
            assessment.encourages_market_analysis,
        ],
        "Instructing_Developing_Capabilities": [
            assessment.estimates_mentor_knowledge,
            assessment.self_assess_abilities,
            assessment.discusses_knowledge_strategies,
            assessment.prefers_active_sessions,
            assessment.discusses_career_options,
        ],
        "Inspiring": [
            assessment.shares_with_classmates,
            assessment.sees_mentor_as_role_model,
            assessment.expects_motivation_support,
            assessment.likes_success_stories,
            assessment.showcases_contributions
        ],
        "Providing_Corrective_Feedback": [
            assessment.discouraged_by_criticism,
            assessment.expects_improvement_feedback,
            assessment.respects_contrary_views,
            assessment.accepts_open_criticism,
            assessment.wants_feedback_grouped,
        ],
        "Managing_Risks": [
            assessment.understands_diff_impacts,
            assessment.considers_industry_exposure,
            assessment.extra_effort_due_to_exposure,
            assessment.supports_experimentation,
            assessment.encouraged_for_projects,
        ],
        "Opening_Doors": [
            assessment.understands_worklife_balance,
            assessment.avoids_using_mentor_network,
            assessment.frequent_meetings,
            assessment.expects_networking_help,
            assessment.supports_industry_interaction
        ]
    }

    results = {
        competency: sum(score for score in scores if score is not None)
        for competency, scores in competency_mapping.items()
    }

    # Update or create competencies record with latest MCA assessment scores
    existing_record = db.query(Competencies).filter(Competencies.student_usn == usn).first()
    if existing_record:
        # Update existing record with new scores from latest MCA submission
        for k, v in results.items():
            setattr(existing_record, k, v)
        print(f"Updated competencies for student {usn} with latest MCA assessment (ID: {assessment.id})")
    else:
        # Create new record with scores from latest MCA submission
        new_record = Competencies(student_usn=usn, **results)
        db.add(new_record)
        print(f"Created new competencies record for student {usn} with latest MCA assessment (ID: {assessment.id})")

    db.commit()
    return {
        "usn": usn, 
        "competency_scores": results,
        "assessment_id": assessment.id,
        "assessment_date": assessment.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        "message": "Competencies updated with latest MCA assessment scores"
    } 