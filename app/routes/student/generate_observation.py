from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.competencies import Competencies
from app.db.models.mentee_competency_report import MenteeCompetencyReport
import re
import time

router = APIRouter()
from app.services.genai_service import model

# Mentor implication logic
def get_mentor_implication(score: int) -> str:
    if 30 <= score <= 35:
        return "Excellent mentor skills; you could coach others; concentrate improvement efforts on fine-tuning your style with particular mentees."
    elif 25 <= score <= 29:
        return "Very good skills; continue to polish those skills that will make you even more effective and desirable as a mentor."
    elif 15 <= score <= 24:
        return "Good skills; you need to work on certain areas of improvement to ensure you are an effective and desirable mentor."
    elif 10 <= score <= 14:
        return "Adequate mentor skills; work on your less-developed skills in order to acquire strong mentees and have better relationships with them."
    elif score <= 9:
        return "You will benefit from coaching and practice on mentor skills; acquire training or coaching, and observe others who have strong skills."
    return "No mentor implication generated."

def generate_with_retry(prompt: str, max_retries: int = 3, initial_delay: float = 2.0):
    """
    Generate content with retry logic for rate limiting (429 errors).
    Uses exponential backoff for retries.
    """
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_str = str(e)
            # Check if it's a 429 rate limit error
            if "429" in error_str or "Resource exhausted" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    # Calculate exponential backoff delay
                    delay = initial_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    # Last attempt failed, raise with helpful message
                    raise HTTPException(
                        status_code=429,
                        detail="API rate limit exceeded. The service is temporarily unavailable due to high demand. Please try again in a few minutes."
                    )
            else:
                # For other errors, raise immediately
                raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    
    # Should not reach here, but just in case
    raise HTTPException(status_code=500, detail="Failed to generate response after retries")

@router.post("/generate_observation_recommendations")
def generate_observation_recommendations(student_usn: str, db: Session = Depends(get_db)):
    competencies = db.query(Competencies).filter(Competencies.student_usn == student_usn).first()
    
    if not competencies:
        raise HTTPException(status_code=404, detail="Competencies not found")

    competency_scores = {
        "Active_Listening": competencies.Active_Listening,
        "Building_Trust": competencies.Building_Trust,
        "Encouraging": competencies.Encouraging,
        "Identifying_Goals_Current_Reality": competencies.Identifying_Goals_Current_Reality,
        "Instructing_Developing_Capabilities": competencies.Instructing_Developing_Capabilities,
        "Inspiring": competencies.Inspiring,
        "Providing_Corrective_Feedback": competencies.Providing_Corrective_Feedback,
        "Managing_Risks": competencies.Managing_Risks,
        "Opening_Doors": competencies.Opening_Doors
    }

    results = []
    
    for idx, (competency, score) in enumerate(competency_scores.items()):
        prompt = f"""The student has demonstrated a competency in {competency}, with a score of {score} out of 35.

Please:

Write one clear, specific observation that reflects the student's strength or a potential area for growth in this competency.

Suggest one actionable recommendation that would help them improve or further develop in this area.

Based on the score, provide one thoughtful mentor implication using the scale below:

Score Guide for Mentor Implications:

30-35 → Excellent mentor skills; you could coach others; concentrate improvement efforts on fine-tuning your style with particular mentees.

25-29 → Very good skills; continue to polish those skills that will make you even more effective and desirable as a mentor.

15-24 → Good skills; you need to work on certain areas of improvement to ensure you are an effective and desirable mentor.

10-14 → Adequate mentor skills; work on your less-developed skills in order to acquire strong mentees and build better relationships.

9 or under → You will benefit from coaching and practice on mentor skills; acquire training or coaching, and observe others who have strong skills.

For the Opening Doors competency specifically, the observation, recommendation, and mentor implication should focus on the student's ability to open doors in terms of creating connections and providing opportunities, not literally opening doors.
Format your response exactly like this:
Observation: <Your observation here>
Recommendation: <Your recommendation here>
Mentor Implication: <Your mentor implication here>"""

        try:
            # Add delay between requests to avoid rate limiting (except for first request)
            # Reduced delay to speed up processing and avoid API Gateway timeout
            if idx > 0:
                time.sleep(0.8)  # Reduced to 0.8 second delay between API calls
            
            response = generate_with_retry(prompt)

            if response and response.candidates:
                text_response = response.candidates[0].content.parts[0].text

                # Extract components
                observation_match = re.search(r"Observation:\s*(.*)", text_response)
                recommendation_match = re.search(r"Recommendation:\s*(.*)", text_response)
                mentor_implication_match = re.search(r"Mentor Implication:\s*(.*)", text_response)

                observation = observation_match.group(1).strip() if observation_match else "No observation generated"
                recommendation = recommendation_match.group(1).strip() if recommendation_match else "No recommendation generated"
                mentor_implication = mentor_implication_match.group(1).strip() if mentor_implication_match else get_mentor_implication(score)
            else:
                observation = recommendation = mentor_implication = "No response generated"

        except HTTPException:
            # Re-raise HTTPExceptions (like 429 errors) as-is
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

        # Save to DB
        new_entry = MenteeCompetencyReport(
            student_usn=student_usn,
            competency=competency,
            observation=observation,
            recommendation=recommendation,
            mentor_implication=mentor_implication
        )
        db.add(new_entry)
        results.append({
            "competency": competency,
            "observation": observation,
            "recommendation": recommendation,
            "mentor_implication": mentor_implication
        })

    db.commit()

    return {
        "message": "Observations, recommendations, and mentor implications generated successfully",
        "data": results
    } 