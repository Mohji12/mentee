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
    
    Returns a JSON response with the following fields:
    - id: Report ID (or None if not saved)
    - student_usn: Student USN
    - professional_aspirations: Professional aspirations text
    - hobbies/interests: Hobbies and interests text
    - strengths: Strengths analysis
    - weaknesses: Weaknesses analysis
    - opportunities: Opportunities analysis
    - threats: Threats analysis
    - detailed_analysis: Detailed summary analysis
    """
    print(f"🚀 Starting SWOT report generation for student: {student_usn}")
    
    # Retrieve the student record to get the current semester
    student = db.query(Student).filter_by(student_usn=student_usn).first()
    if not student:
        print(f"❌ Student not found: {student_usn}")
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
        
        # Prepare data for SWOT analysis generation (handle None values)
        def safe_get(attr):
            return getattr(student_data, attr, None) or "Not specified"
        
        data = {
            "subjects_strength": safe_get("subjects_strength"),
            "subjects_weakness": safe_get("subjects_weakness"),
            "previous_work_experience": safe_get("previous_work_experience"),
            "professional_dream": safe_get("professional_dream"),
            "professional_fear": safe_get("professional_fear"),
            "happiness_sources": safe_get("happiness_sources"),
            "expectations": safe_get("expectations"),
            "goal_achieving_opportunities": safe_get("goal_achieving_opportunities"),
            "participate_in_skill_programs": safe_get("participate_in_skill_programs"),
            "interested_skill_programs": safe_get("interested_skill_programs"),
            "external_factors_affecting_growth": safe_get("external_factors_affecting_growth"),
            "primary_stressors": safe_get("primary_stressors"),
            "biggest_distractions": safe_get("biggest_distractions"),
            "strongest_skills": safe_get("strongest_skills"),
            "areas_of_low_confidence": safe_get("areas_of_low_confidence"),
            "hobbies_interests": safe_get("hobbies_interests"),
        }
        
        # Generate SWOT analysis and activity suggestions
        print(f"🔄 Generating SWOT analysis for student {student_usn}...")
        analysis = generate_analysis_and_activities(data)
        print(f"📝 Generated analysis length: {len(analysis) if analysis else 0}")
        if not analysis or analysis == "No analysis or suggestions available.":
            raise HTTPException(status_code=500, detail="Failed to generate SWOT analysis. Please try again later.")

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
    
    try:
        parsed_swot = parse_swot_analysis(swot_report.swot_analysis)
        print(f"✅ Parsed SWOT data keys: {list(parsed_swot.keys())}")
        
        # Validate that we got meaningful data (not all "Not specified")
        not_specified_count = sum(1 for value in parsed_swot.values() if value == "Not specified")
        if not_specified_count == len(parsed_swot):
            error_msg = f"Failed to parse SWOT analysis. All fields returned 'Not specified'. This indicates the parsing logic couldn't extract data from the generated text."
            print(f"❌ {error_msg}")
            print(f"📄 Full SWOT analysis text:\n{swot_report.swot_analysis}")
            raise HTTPException(status_code=500, detail=error_msg)
        elif not_specified_count > 0:
            print(f"⚠️ Warning: {not_specified_count} out of {len(parsed_swot)} fields failed to parse")
    except Exception as e:
        print(f"❌ Error parsing SWOT analysis: {str(e)}")
        print(f"📄 SWOT analysis text:\n{swot_report.swot_analysis[:1000]}")
        raise HTTPException(status_code=500, detail=f"Error parsing SWOT analysis: {str(e)}")

    # Check if the report already exists for the student
    # Note: We check by student_usn only, not by semester, to allow updates
    existing_report = db.query(Report).filter_by(student_usn=student_usn).first()
    if existing_report:
        print(f"📝 Updating existing report for student {student_usn}")
        try:
            # If a report already exists, update it with the new parsed data
            existing_report.professional_aspirations = parsed_swot["professional_aspirations"]
            existing_report.hobbies_interests = parsed_swot["hobbies/interests"]
            existing_report.strengths = parsed_swot["strengths"]
            existing_report.weaknesses = parsed_swot["weaknesses"]
            existing_report.opportunities = parsed_swot["opportunities"]
            existing_report.threats = parsed_swot["threats"]
            existing_report.detailed_analysis = parsed_swot["detailed_analysis"]
            db.commit()
            db.refresh(existing_report)  # Refresh to get updated data
            print(f"✅ Report updated successfully with ID: {existing_report.id}")
            
            # Verify the data was saved
            print(f"📊 Verification - Saved data preview:")
            print(f"  Professional Aspirations: {existing_report.professional_aspirations[:50] if existing_report.professional_aspirations else 'None'}...")
            print(f"  Strengths: {existing_report.strengths[:50] if existing_report.strengths else 'None'}...")
            
            response_data = {
                "id": existing_report.id,
                "student_usn": existing_report.student_usn,
                "professional_aspirations": existing_report.professional_aspirations or "",
                "hobbies/interests": existing_report.hobbies_interests or "",
                "strengths": existing_report.strengths or "",
                "weaknesses": existing_report.weaknesses or "",
                "opportunities": existing_report.opportunities or "",
                "threats": existing_report.threats or "",
                "detailed_analysis": existing_report.detailed_analysis or "",
            }
            print(f"📤 Returning response with {len([v for v in response_data.values() if v])} non-empty fields")
            return response_data
        except Exception as e:
            db.rollback()
            print(f"❌ Error updating report: {str(e)}")
            # Fallback: Return parsed data even if database update fails
            print(f"🔄 Attempting to return parsed data as fallback...")
            return {
                "id": existing_report.id if existing_report else None,
                "student_usn": student_usn,
                "professional_aspirations": parsed_swot.get("professional_aspirations", ""),
                "hobbies/interests": parsed_swot.get("hobbies/interests", ""),
                "strengths": parsed_swot.get("strengths", ""),
                "weaknesses": parsed_swot.get("weaknesses", ""),
                "opportunities": parsed_swot.get("opportunities", ""),
                "threats": parsed_swot.get("threats", ""),
                "detailed_analysis": parsed_swot.get("detailed_analysis", ""),
            }

    # If no report exists, create a new one
    print(f"📝 Creating new report for student {student_usn}")
    try:
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
        db.refresh(new_report)  # Refresh to get the ID and verify data
        print(f"✅ New report created successfully with ID: {new_report.id}")
        
        # Verify the data was saved
        print(f"📊 Verification - Saved data preview:")
        print(f"  Professional Aspirations: {new_report.professional_aspirations[:50] if new_report.professional_aspirations else 'None'}...")
        print(f"  Strengths: {new_report.strengths[:50] if new_report.strengths else 'None'}...")

        # Return the newly generated report
        response_data = {
            "id": new_report.id,
            "student_usn": new_report.student_usn,
            "professional_aspirations": new_report.professional_aspirations or "",
            "hobbies/interests": new_report.hobbies_interests or "",
            "strengths": new_report.strengths or "",
            "weaknesses": new_report.weaknesses or "",
            "opportunities": new_report.opportunities or "",
            "threats": new_report.threats or "",
            "detailed_analysis": new_report.detailed_analysis or "",
        }
        non_empty_count = len([v for v in response_data.values() if v and v != ""])
        print(f"📤 Returning response with {non_empty_count} non-empty fields out of {len(response_data)} total fields")
        print(f"📋 Response keys: {list(response_data.keys())}")
        return response_data
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating report: {str(e)}")
        # Fallback: Return parsed data even if database save fails
        print(f"🔄 Attempting to return parsed data as fallback...")
        return {
            "id": None,
            "student_usn": student_usn,
            "professional_aspirations": parsed_swot.get("professional_aspirations", ""),
            "hobbies/interests": parsed_swot.get("hobbies/interests", ""),
            "strengths": parsed_swot.get("strengths", ""),
            "weaknesses": parsed_swot.get("weaknesses", ""),
            "opportunities": parsed_swot.get("opportunities", ""),
            "threats": parsed_swot.get("threats", ""),
            "detailed_analysis": parsed_swot.get("detailed_analysis", ""),
        }