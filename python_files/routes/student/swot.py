from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.swot import SWOT
from app.db.models.report import Report
from app.db.models.psychometric_responses import PsychometricResponse
from app.utils.analysis import generate_analysis_and_activities, parse_activities, parse_swot_analysis

router = APIRouter()

@router.get("/swot-report")
def generate_swot_report(student_usn: str, db: Session = Depends(get_db)):
    """
    Fetch or generate the SWOT report for a specific student using their USN.
    """
    # Retrieve the student record to get the current semester
    student = db.query(Student).filter_by(student_usn=student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {student_usn}")
    
    # Check if the SWOT analysis already exists for the current semester
    swot_report = (
        db.query(SWOT)
        .join(Student, SWOT.student_usn == Student.student_usn)
        .filter(SWOT.student_usn == student_usn, Student.semester == student.semester)
        .first()
    )
    
    if not swot_report:
        # Retrieve the psychometric responses for the student
        student_data = db.query(PsychometricResponse).filter_by(student_usn=student_usn).first()
        if not student_data:
            raise HTTPException(status_code=404, detail=f"No psychometric data found for student USN {student_usn}")
        
        # Prepare data for SWOT analysis generation
        data = {
            "subjects_strength": student_data.subjects_strength,
            "subjects_weakness": student_data.subjects_weakness,
            "previous_work_experience": student_data.previous_work_experience,
            "professional_dream": student_data.professional_dream,
            "professional_fear": student_data.professional_fear,
            "happiness_sources": student_data.happiness_sources,
            "expectations": student_data.expectations,
            "goal_achieving_opportunities": student_data.goal_achieving_opportunities,
            "participate_in_skill_programs": student_data.participate_in_skill_programs,
            "interested_skill_programs": student_data.interested_skill_programs,
            "external_factors_affecting_growth": student_data.external_factors_affecting_growth,
            "primary_stressors": student_data.primary_stressors,
            "biggest_distractions": student_data.biggest_distractions,
            "strongest_skills": student_data.strongest_skills,
            "areas_of_low_confidence": student_data.areas_of_low_confidence,
            "hobbies_interests": student_data.hobbies_interests,
        }
        
        # Generate SWOT analysis and activity suggestions
        analysis = generate_analysis_and_activities(data)

        # Parse activities
        activities = parse_activities(analysis)

        # Store the SWOT analysis in the 'swot' table
        swot_report = SWOT(student_usn=student_usn, swot_analysis=analysis)
        db.add(swot_report)
        db.commit()

    # Parse the SWOT analysis to extract relevant fields
    print(f"🔍 Parsing SWOT analysis for student {student_usn}")
    print(f"📄 SWOT analysis length: {len(swot_report.swot_analysis) if swot_report.swot_analysis else 0}")
    print(f"📄 SWOT analysis preview: {swot_report.swot_analysis[:200] if swot_report.swot_analysis else 'None'}...")
    
    parsed_swot = parse_swot_analysis(swot_report.swot_analysis)
    print(f"✅ Parsed SWOT data: {parsed_swot}")

    # Check if the report already exists for the student in the current semester
    existing_report = db.query(Report).filter_by(student_usn=student_usn).first()
    if existing_report:
        print(f"📝 Updating existing report for student {student_usn}")
        # If a report already exists, update it with the new parsed data
        existing_report.professional_aspirations = parsed_swot["professional_aspirations"]
        existing_report.hobbies_interests = parsed_swot["hobbies/interests"]
        existing_report.strengths = parsed_swot["strengths"]
        existing_report.weaknesses = parsed_swot["weaknesses"]
        existing_report.opportunities = parsed_swot["opportunities"]
        existing_report.threats = parsed_swot["threats"]
        existing_report.detailed_analysis = parsed_swot["detailed_analysis"]
        db.commit()
        print(f"✅ Report updated successfully")
        return {
            "id": existing_report.id,
            "student_usn": existing_report.student_usn,
            "professional_aspirations": existing_report.professional_aspirations,
            "hobbies/interests": existing_report.hobbies_interests,
            "strengths": existing_report.strengths,
            "weaknesses": existing_report.weaknesses,
            "opportunities": existing_report.opportunities,
            "threats": existing_report.threats,
            "detailed_analysis": existing_report.detailed_analysis,
        }

    # If no report exists, create a new one
    print(f"📝 Creating new report for student {student_usn}")
    new_report = Report(
        student_usn=student_usn,
        professional_aspirations=parsed_swot["professional_aspirations"],
        hobbies_interests=parsed_swot["hobbies/interests"],
        strengths=parsed_swot["strengths"],
        weaknesses=parsed_swot["weaknesses"],
        opportunities=parsed_swot["opportunities"],
        threats=parsed_swot["threats"],
        detailed_analysis=parsed_swot["detailed_analysis"],
    )
    db.add(new_report)
    db.commit()
    print(f"✅ New report created successfully with ID: {new_report.id}")

    # Return the newly generated report
    return {
        "id": new_report.id,
        "student_usn": new_report.student_usn,
        "professional_aspirations": new_report.professional_aspirations,
        "hobbies/interests": new_report.hobbies_interests,
        "strengths": new_report.strengths,
        "weaknesses": new_report.weaknesses,
        "opportunities": new_report.opportunities,
        "threats": new_report.threats,
        "detailed_analysis": new_report.detailed_analysis,
    }