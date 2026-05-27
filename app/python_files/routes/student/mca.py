from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.students import Student
from app.db.database import get_db
from app.schemas.mca_assignment import MentoringAssessment
from datetime import datetime, date, timedelta

router = APIRouter()

@router.get("/mca-questions")
async def get_mca_questions():
    """Get all MCA questions with their aliases and internal field names"""
    questions = [
        # Page 1 (8 questions)
        {"alias": "listens_carefully", "question": "I listen to my Mentor carefully even if they talk elaborately repeating things again and again.", "internal_name": "listens_carefully"},
        {"alias": "discouraged_by_criticism", "question": "I always Provide constructive feedback to mentor without discouraging them", "internal_name": "discouraged_by_criticism"},
        {"alias": "builds_trust", "question": "I take conscious steps to Establish a relationship based on trust with my mentor", "internal_name": "builds_trust"},
        {"alias": "adapts_to_styles", "question": "I adapt to identifying and accommodating different communication styles with mentor", "internal_name": "adapts_to_styles"},
        {"alias": "shares_with_classmates", "question": "I Coordinate effectively with other mentors for improving mentoring effectiveness", "internal_name": "shares_with_classmates"},
        {"alias": "sets_expectations", "question": "I Work with mentor to set clear expectations of the mentoring relationship", "internal_name": "sets_expectations"},
        {"alias": "aligns_expectations", "question": "I Align my expectations with my mentor for a better mentoring effectiveness*", "internal_name": "aligns_expectations", "has_asterisk": True},
        {"alias": "wants_mentor_to_adapt", "question": "I adapt to different communication style to suit the comfort of mentees communication *", "internal_name": "wants_mentor_to_adapt", "has_asterisk": True},
        
        # Page 2 (8 questions)
        {"alias": "expects_improvement_feedback", "question": "I point out areas of improvements while they discuss their difficulties with me", "internal_name": "expects_improvement_feedback"},
        {"alias": "understands_diff_impacts", "question": "I understand how personal and professional differences impact expectations", "internal_name": "understands_diff_impacts"},
        {"alias": "goal_setting_with_mentor", "question": "I Work along with my mentor to set my goals*", "internal_name": "goal_setting_with_mentor", "has_asterisk": True},
        {"alias": "sees_mentor_as_role_model", "question": "I ensure unblemished image as a role model to my mentors", "internal_name": "sees_mentor_as_role_model"},
        {"alias": "aligns_with_industry_expectations", "question": "I check mentors expectations and align industry expectations for a better employability", "internal_name": "aligns_with_industry_expectations"},
        {"alias": "polite_repetition_reminder", "question": "I politely remind mentees if they explain same issues repeatedly to ensure time sense *", "internal_name": "polite_repetition_reminder", "has_asterisk": True},
        {"alias": "estimates_mentor_knowledge", "question": "I accurately estimate mentees' level of scientific knowledge by closely interacting with them", "internal_name": "estimates_mentor_knowledge"},
        {"alias": "considers_industry_exposure", "question": "I consider the mentees exposure while explaining industry expectations to them *", "internal_name": "considers_industry_exposure", "has_asterisk": True},
        
        # Page 3 (8 questions)
        {"alias": "self_assess_abilities", "question": "I accurately estimate each mentee's ability right at the beginning of the session itself *", "internal_name": "self_assess_abilities", "has_asterisk": True},
        {"alias": "understands_worklife_balance", "question": "I emphasis importance of Work-Life- balance to mentors", "internal_name": "understands_worklife_balance"},
        {"alias": "discusses_knowledge_strategies", "question": "I discuss various strategies to enhance mentees' knowledge and abilities", "internal_name": "discusses_knowledge_strategies"},
        {"alias": "avoids_using_mentor_network", "question": "I do not use my mentor's network for improving my network fearing my mentor's connections may not like it *", "internal_name": "avoids_using_mentor_network", "has_asterisk": True},
        {"alias": "discusses_goal_strategies", "question": "I discuss various strategies with my mentors to achieve my goals", "internal_name": "discusses_goal_strategies"},
        {"alias": "improves_communication", "question": "I employ various strategies to improve communication with my mentors", "internal_name": "improves_communication"},
        {"alias": "stays_self_motivated", "question": "I always ensure that we are kept motivated by mentors", "internal_name": "stays_self_motivated"},
        {"alias": "discusses_career_options", "question": "I keep discussing various career options available with my mentors in line with their expertise", "internal_name": "discusses_career_options"},
        
        # Page 4 (8 questions)
        {"alias": "frequent_meetings", "question": "I keep discussing encouraging stories with my mentors to build confidence high", "internal_name": "frequent_meetings"},
        {"alias": "extra_effort_due_to_exposure", "question": "I strongly put forward industry expectations considering mentors low industry exposure *", "internal_name": "extra_effort_due_to_exposure", "has_asterisk": True},
        {"alias": "prefers_active_sessions", "question": "I provide activated situations to Stimulate mentees' creativity during the sessions", "internal_name": "prefers_active_sessions"},
        {"alias": "seeks_networking_support", "question": "My mentors provide support through their network to improve my networking", "internal_name": "seeks_networking_support"},
        {"alias": "wants_showcasing_contributions", "question": "I showcase mentors professional contributions at appropriate situations in their presence", "internal_name": "wants_showcasing_contributions"},
        {"alias": "handles_background_differences", "question": "I effectively deal with my mentors even when their age and personal background are different", "internal_name": "handles_background_differences"},
        {"alias": "expects_independence", "question": "I provide professional independence to mentees even at the cost of doing mistakes", "internal_name": "expects_independence"},
        {"alias": "wants_feedback_grouped", "question": "I study mentors capabilities and classify them in to different groups to give critical feedbacks *", "internal_name": "wants_feedback_grouped", "has_asterisk": True},
        
        # Page 5 (8 questions)
        {"alias": "avoids_bias_prejudice", "question": "I take extra care not to bias and prejudice the mentor/mentee relationship at any time", "internal_name": "avoids_bias_prejudice"},
        {"alias": "expects_motivation_support", "question": "I make it a point to motivate mentors especially during difficult times", "internal_name": "expects_motivation_support"},
        {"alias": "works_with_diverse_mentors", "question": "I Work comfortably with mentors even when their personal background is different from mine", "internal_name": "works_with_diverse_mentors"},
        {"alias": "likes_success_stories", "question": "I encourage my mentor to discuss stories of successful people to boost my confidence level", "internal_name": "likes_success_stories"},
        {"alias": "expects_networking_help", "question": "I provide support to mentees to improve their network effectively", "internal_name": "expects_networking_help"},
        {"alias": "encouraged_for_projects", "question": "I encourage mentors to take up new projects even if they do not have complete knowledge about the subject.", "internal_name": "encouraged_for_projects"},
        {"alias": "expects_career_exposure", "question": "My mentors Helps me to set career goals by exposing them to various options available", "internal_name": "expects_career_exposure"},
        {"alias": "supports_experimentation", "question": "I encourage mentors to experiment new ideas even at the cost of failure during new projects", "internal_name": "supports_experimentation"},
        
        # Page 6 (5 questions)
        {"alias": "supports_industry_interaction", "question": "I encourage mentees to initiate industry interaction to get more exposure with professionals", "internal_name": "supports_industry_interaction"},
        {"alias": "respects_contrary_views", "question": "I give weightage to my views when mentees views are contradicting knowing their lack of experience *", "internal_name": "respects_contrary_views", "has_asterisk": True},
        {"alias": "encourages_market_analysis", "question": "I encourage mentors to analyze the current job market to understand market realities", "internal_name": "encourages_market_analysis"},
        {"alias": "showcases_contributions", "question": "I take efforts to showcase mentees professional contributions in front of my colleagues", "internal_name": "showcases_contributions"},
        {"alias": "accepts_open_criticism", "question": "I openly criticize mentees for their mistakes even at the risk of demotivating them temporarily *", "internal_name": "accepts_open_criticism", "has_asterisk": True}
    ]
    return questions

@router.get("/mca-lock-status")
async def get_mca_lock_status(student_usn: str, db: Session = Depends(get_db)):
    """Check if MCA form is locked and when it can be submitted again"""
    
    # Get the student from the database
    student = db.query(Student).filter_by(student_usn=student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check for last submission
    last_submission = db.query(MentorshipAssessment).filter(
        MentorshipAssessment.student_usn == student_usn
    ).order_by(MentorshipAssessment.submitted_at.desc()).first()
    
    if not last_submission:
        return {
            "is_locked": False,
            "can_submit": True,
            "message": "No previous submission found. You can submit the MCA form."
        }
    
    # Calculate lock period
    lock_period_end = last_submission.submitted_at + timedelta(days=60)  # 2 months
    current_time = datetime.utcnow()
    
    if current_time < lock_period_end:
        days_remaining = (lock_period_end - current_time).days
        hours_remaining = ((lock_period_end - current_time).total_seconds() // 3600) % 24
        
        return {
            "is_locked": True,
            "can_submit": False,
            "last_submission": last_submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            "lock_ends": lock_period_end.strftime('%Y-%m-%d %H:%M:%S'),
            "days_remaining": days_remaining,
            "hours_remaining": int(hours_remaining),
            "message": f"MCA form is locked. You can submit again in {days_remaining} days and {int(hours_remaining)} hours."
        }
    else:
        return {
            "is_locked": False,
            "can_submit": True,
            "last_submission": last_submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            "message": "Lock period has expired. You can submit the MCA form again."
        }

@router.post("/mca-form")
async def submit_mca_form(student_usn: str, form: MentoringAssessment, db: Session = Depends(get_db)):
    """Submit MCA form with proper field mapping and score reversal for asterisk questions"""
    
    # Step 1: Get the student from the database
    student = db.query(Student).filter_by(student_usn=student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Step 1.5: Check for 2-month lock period
    last_submission = db.query(MentorshipAssessment).filter(
        MentorshipAssessment.student_usn == student_usn
    ).order_by(MentorshipAssessment.submitted_at.desc()).first()
    
    if last_submission:
        # Calculate 2 months from last submission
        lock_period_end = last_submission.submitted_at + timedelta(days=60)  # 2 months = 60 days
        current_time = datetime.utcnow()
        
        if current_time < lock_period_end:
            days_remaining = (lock_period_end - current_time).days
            hours_remaining = ((lock_period_end - current_time).total_seconds() // 3600) % 24
            
            raise HTTPException(
                status_code=423,  # 423 Locked
                detail=f"MCA form is locked for 2 months after submission. You can submit again in {days_remaining} days and {int(hours_remaining)} hours. Last submission was on {last_submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    # Step 2: Get the form data as a dictionary
    form_data = form.dict(by_alias=False)
    
    print(f"Received form data: {form_data}")
    print(f"Form data keys: {list(form_data.keys())}")
    print(f"Form data values: {list(form_data.values())}")
    print(f"Total fields received: {len(form_data)}")
    
    # Check if all required fields are present
    required_fields = {
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
    }
    
    missing_fields = required_fields - set(form_data.keys())
    extra_fields = set(form_data.keys()) - required_fields
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
    else:
        print("✅ All required fields present")
        
    if extra_fields:
        print(f"⚠️ Extra fields received: {extra_fields}")
    else:
        print("✅ No extra fields")
    
    # Step 3: Define questions with asterisks that need score reversal
    asterisk_questions = {
        "aligns_expectations",
        "wants_mentor_to_adapt", 
        "goal_setting_with_mentor",
        "polite_repetition_reminder",
        "considers_industry_exposure",
        "self_assess_abilities",
        "avoids_using_mentor_network",
        "extra_effort_due_to_exposure",
        "wants_feedback_grouped",
        "respects_contrary_views",
        "accepts_open_criticism"
    }
    
    # Step 4: Function to convert and validate scores
    def process_score(score):
        """Convert score to integer: 'NA' -> 0, strings -> integers, validate range"""
        try:
            # Handle 'NA' or 'na' values
            if str(score).upper() == 'NA':
                return 0
            
            # Convert to integer
            score_int = int(score)
            
            # Validate range (1-7)
            if score_int < 1 or score_int > 7:
                print(f"Warning: Score {score_int} is out of range (1-7), setting to 0")
                return 0
                
            return score_int
        except (ValueError, TypeError):
            print(f"Warning: Could not convert score '{score}' to integer, setting to 0")
            return 0
    
    # Step 5: Function to reverse scores based on the formula
    def reverse_score(score):
        """Reverse score: 1->7, 2->6, 3->5, 4->4, 5->3, 6->2, 7->1"""
        if score == 0:  # Handle 0 (converted from NA)
            return 0
        elif score == 1: return 7
        elif score == 2: return 6
        elif score == 3: return 5
        elif score == 4: return 4  # stays the same
        elif score == 5: return 3
        elif score == 6: return 2
        elif score == 7: return 1
        else: return score  # for any other values, keep as is
    
    # Step 6: Process form data and reverse scores for asterisk questions
    processed_data = {}
    
    print("Processing form data for score conversion and reversal...")
    print(f"Asterisk questions: {asterisk_questions}")
    
    for field_name, value in form_data.items():
        print(f"Processing field: {field_name} | Value: {value} | Type: {type(value)}")
        
        # First, convert and validate the score
        processed_score = process_score(value)
        print(f"🔄 CONVERTED: {field_name} | Original: {value} -> Processed: {processed_score}")
        
        if field_name in asterisk_questions:
            # Apply score reversal for questions with asterisks
            reversed_score = reverse_score(processed_score)
            processed_data[field_name] = reversed_score
            print(f"✅ REVERSED: {field_name} | Processed: {processed_score} -> Reversed: {reversed_score}")
        else:
            # Keep processed score for questions without asterisks
            processed_data[field_name] = processed_score
            print(f"➡️ KEPT: {field_name} | Final Score: {processed_score}")

    # Step 7: Create a new MCA response entry with processed data
    new_response = MentorshipAssessment(
        student_usn=student_usn,
        **processed_data
    )

    # Step 8: Add the new response to the database and commit
    try:
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
        print(f"✅ MCA form submitted successfully for student {student_usn}")
        return {"message": "MCA form submitted successfully", "id": new_response.id}
    except Exception as e:
        db.rollback()
        print(f"❌ Error submitting MCA form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit MCA form: {str(e)}") 