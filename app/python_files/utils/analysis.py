import re
from app.services.genai_service import model

def parse_swot_analysis(swot_analysis: str):
    """
    Parse SWOT analysis text and extract individual sections.
    This function handles multiple possible formats of the generated analysis.
    """
    if not swot_analysis or not isinstance(swot_analysis, str):
        return {
            "professional_aspirations": "Not specified",
            "hobbies/interests": "Not specified", 
            "strengths": "Not specified",
            "weaknesses": "Not specified",
            "opportunities": "Not specified",
            "threats": "Not specified",
            "detailed_analysis": "Not specified",
        }
    
    # Define multiple possible patterns for each section to handle different formats
    patterns = {
        "professional_aspirations": [
            r"\*\*Professional Aspirations\*\*:?\s*(.*?)(?=\*\*Skills/Interests/Hobbies\*\*|\*\*Strengths\*\*|\Z)",
            r"Professional Aspirations:?\s*(.*?)(?=Skills/Interests/Hobbies|Strengths|\Z)",
            r"**Professional Aspirations**:?\s*(.*?)(?=**Skills/Interests/Hobbies**|**Strengths**|\Z)"
        ],
        "hobbies/interests": [
            r"\*\*Skills/Interests/Hobbies\*\*:?\s*(.*?)(?=\*\*Strengths\*\*|\*\*Weaknesses\*\*|\Z)",
            r"Skills/Interests/Hobbies:?\s*(.*?)(?=Strengths|Weaknesses|\Z)",
            r"**Skills/Interests/Hobbies**:?\s*(.*?)(?=**Strengths**|**Weaknesses**|\Z)"
        ],
        "strengths": [
            r"\*\*Strengths\*\*:?\s*(.*?)(?=\*\*Weaknesses\*\*|\*\*Opportunities\*\*|\Z)",
            r"Strengths:?\s*(.*?)(?=Weaknesses|Opportunities|\Z)",
            r"**Strengths**:?\s*(.*?)(?=**Weaknesses**|**Opportunities**|\Z)"
        ],
        "weaknesses": [
            r"\*\*Weaknesses\*\*:?\s*(.*?)(?=\*\*Opportunities\*\*|\*\*Threats\*\*|\Z)",
            r"Weaknesses:?\s*(.*?)(?=Opportunities|Threats|\Z)",
            r"**Weaknesses**:?\s*(.*?)(?=**Opportunities**|**Threats**|\Z)"
        ],
        "opportunities": [
            r"\*\*Opportunities\*\*:?\s*(.*?)(?=\*\*Threats\*\*|\*\*Detailed Summary Analysis\*\*|\Z)",
            r"Opportunities:?\s*(.*?)(?=Threats|Detailed Summary Analysis|\Z)",
            r"**Opportunities**:?\s*(.*?)(?=**Threats**|**Detailed Summary Analysis**|\Z)"
        ],
        "threats": [
            r"\*\*Threats\*\*:?\s*(.*?)(?=\*\*Detailed Summary Analysis\*\*|\*\*Activities\*\*|\Z)",
            r"Threats:?\s*(.*?)(?=Detailed Summary Analysis|Activities|\Z)",
            r"**Threats**:?\s*(.*?)(?=**Detailed Summary Analysis**|**Activities**|\Z)"
        ],
        "detailed_analysis": [
            r"\*\*Detailed Summary Analysis\*\*:?\s*(.*?)(?=\*\*Activities\*\*|Activities to Improve Performance|\Z)",
            r"Detailed Summary Analysis:?\s*(.*?)(?=Activities|Activities to Improve Performance|\Z)",
            r"**Detailed Summary Analysis**:?\s*(.*?)(?=**Activities**|Activities to Improve Performance|\Z)"
        ]
    }

    def clean_text(text):
        """Clean and format extracted text"""
        if not text:
            return "Not specified"
        
        # Remove markdown formatting
        text = re.sub(r'\*\*', '', text)  # Remove bold markers
        text = re.sub(r'\*', '', text)    # Remove italic markers
        text = re.sub(r'#+', '', text)    # Remove headers
        text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)  # Remove bullet points
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
        
        # Clean up whitespace and special characters
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)  # Remove special characters except basic punctuation
        
        return text if text.strip() else "Not specified"

    def extract_section(section_name):
        """Try multiple patterns to extract a section"""
        for pattern in patterns[section_name]:
            match = re.search(pattern, swot_analysis, re.DOTALL | re.IGNORECASE)
            if match and match.group(1).strip():
                return clean_text(match.group(1))
        return "Not specified"

    # Extract all sections
    result = {}
    for section_name in patterns.keys():
        result[section_name] = extract_section(section_name)
    
    return result

# Helper function to generate SWOT analysis and activities
def generate_analysis_and_activities(row):
    prompt = (
        f"Here is information about a student:\n\n"
        f"Subjects Strengths: {row['subjects_strength']}\n"
        f"Subject Weakness: {row['subjects_weakness']}\n"
        f"Previous Work Experience: {row['previous_work_experience']}\n"
        f"Professional Dream: {row['professional_dream']}\n"
        f"Professional Fear: {row['professional_fear']}\n"
        f"Happiness Sources: {row['happiness_sources']}\n\n"
        f"Expectations when joining Jain University Deemed to be college: {row['expectations']}\n"
        f"Goal Achieving Opportunities: {row['goal_achieving_opportunities']}\n"
        f"Interested in Skills Program: {row['participate_in_skill_programs']}\n"
        f"Skills Program to Participate: {row['interested_skill_programs']}\n"
        f"External Factors affecting growth: {row['external_factors_affecting_growth']}\n"
        f"Primary Stressors: {row['primary_stressors']}\n\n"
        f"Biggest Distractions: {row['biggest_distractions']}\n"
        f"Strongest Skills: {row['strongest_skills']}\n"
        f"Areas of low confidence: {row['areas_of_low_confidence']}\n"
        f"Hobbies/Interests: {row['hobbies_interests']}\n\n"
        f"1. Conduct a SWOT (Strengths, Weaknesses, Opportunities, and Threats) analysis for this student. Report should include bullets sections that are Professional Aspirations, Skills/Interests/Hobbies, Strengths, Weaknesses, Opportunities, Threats, and Detailed Summary Analysis.\n"
        f"2. Based on this information, suggest 3 targeted activities to enhance the student's performance. Organize these activities into three distinct terms and divide it into short term (0-3 Months), mid term (3-6 Months), and long term (7-12 Months). For each term, **suggest at least three supporting platforms, institutions, or credible sources** that can help the student achieve these goals. Do not list them under 'Sources' but integrate them naturally within the activity descriptions."
        f"So format should go like this for the swot analysis."
        f"**Professional Aspirations**"
        f"Clearly describe the student's career ambitions and motivations. How do their current skills, experiences, and educational background align with these aspirations? What gaps need to be filled?"
        f"**Skills/Interests/Hobbies**"
        f"Discuss how the student’s existing skills and hobbies contribute to their personal growth, mental well-being, and professional preparedness. Highlight any transferable skills from hobbies to their career goals.."
        f"**Strengths**"
        f"Provide an **in-depth** explanation of the student's key strengths in both academic and professional contexts. Discuss how these strengths contribute to their ability to succeed in their field and how they can be further leveraged."
        f"**Weaknesses**"
        f"Identify areas where the student lacks confidence or struggles. Go beyond listing weaknesses—explain **why** these are weaknesses and how they impact their academic, personal, and professional progress. Provide **context and examples."
        f"**Opportunities**"
        f"Analyze available opportunities that the student can leverage to achieve success. Include institutional resources (college programs, faculty mentorship, networking events), external platforms (online courses, internships, competitions), and personal strategies."
        f"**Threats**"
        f"Describe the key challenges that could hinder the student’s progress. Consider industry-related threats (rapid technological advancements, job market competition), academic barriers, and personal hurdles such as procrastination or lack of mentorship."
        f"**Detailed Summary Analysis**"
        f"Conclude with a strategic evaluation of how the student can best navigate their strengths and weaknesses while capitalizing on opportunities and mitigating threats. Summarize key takeaways and outline a roadmap for improvement."
        f"**Activities**"
        f"**Short Term (0-2 Months):**"
        f"Recommend 3 specific activities that the student can immediately implement. Focus on skill-building, networking, and habit formation. Each activity should be actionable and impactful."
        f"**Mid Term (3-6 Months):**"
        f"Suggest 3 mid-term activities that provide deeper learning experiences. These should focus on hands-on applications, real-world exposure (internships, research projects, hackathons), and building a professional presence (LinkedIn, portfolio development)."
        f"**Long Term (7-12 Months):**"
        f"Provide 3 structured long-term activities that help the student solidify their career trajectory. These should include high-impact professional networking, deeper technical skill development, and strategic career planning."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No analysis or suggestions available."
    except Exception as e:
        print(f"Error generating analysis and activities: {e}")
        return "No analysis or suggestions available."

def parse_activities(analysis):
    # Define the regex pattern to capture activities under each term
    short_term_pattern = r"\*\*Short Term \(\d+-\d+ Months\):\*\*(.*?)(?=\*\*Mid Term|\*\*Long Term|\Z)"
    mid_term_pattern = r"\*\*Mid Term \(\d+-\d+ Months\):\*\*(.*?)(?=\*\*Short Term|\*\*Long Term|\Z)"
    long_term_pattern = r"\*\*Long Term \(\d+-\d+ Months\):\*\*(.*?)(?=\*\*Short Term|\*\*Mid Term|\Z)"

    # Function to clean and split the text into multiple activities, removing any numbers, asterisks, and extra spaces
    def clean_and_split(text):
        # Remove numbers at the start of each line (1., 2., 3., etc.)
        cleaned_text = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE)
        
        # Remove all asterisks from the text
        cleaned_text = cleaned_text.replace("*", "")  # Remove all asterisks

        # Remove extra spaces and trim the text
        cleaned_text = cleaned_text.strip()

        # Split into activities based on new lines and strip extra spaces around them
        activities = [activity.strip() for activity in cleaned_text.split("\n") if activity.strip()]

        # Ensure we always return exactly 3 activities per section, padding with empty strings if necessary
        return activities[:3] + [""] * (3 - len(activities))

    # Extract the sections based on the defined patterns
    short_term = re.search(short_term_pattern, analysis, re.DOTALL)
    mid_term = re.search(mid_term_pattern, analysis, re.DOTALL)
    long_term = re.search(long_term_pattern, analysis, re.DOTALL)

    # Parse each term's activities, or use a default if no activities found
    result = {
        "short_term": clean_and_split(short_term.group(1)) if short_term else ["No activities found"] * 3,
        "mid_term": clean_and_split(mid_term.group(1)) if mid_term else ["No activities found"] * 3,
        "long_term": clean_and_split(long_term.group(1)) if long_term else ["No activities found"] * 3
    }

    # Ensure no section contains empty strings (replace with "No activities found")
    for key in result:
        result[key] = [activity if activity else "No activities found" for activity in result[key]]

    return result
