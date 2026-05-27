import re
from app.services.genai_service import model

def parse_swot_analysis(swot_analysis: str):
    """
    Parse SWOT analysis text and extract structured sections.
    Handles various formatting variations from AI-generated text.
    """
    if not swot_analysis or not isinstance(swot_analysis, str):
        print("⚠️ Warning: Empty or invalid SWOT analysis provided")
        return {
            "professional_aspirations": "Not specified",
            "hobbies/interests": "Not specified",
            "strengths": "Not specified",
            "weaknesses": "Not specified",
            "opportunities": "Not specified",
            "threats": "Not specified",
            "detailed_analysis": "Not specified",
        }
    
    # Print first 1000 chars for debugging
    print(f"📄 SWOT Analysis Text Preview (first 1000 chars):\n{swot_analysis[:1000]}\n...")
    
    # More flexible patterns that handle various formats:
    # - Headers with or without ** markdown
    # - Headers with or without colons
    # - Case-insensitive matching
    # - Headers on same line or next line
    # - Handle variations in spacing and newlines
    
    # Pattern variations for each section - try multiple formats
    professional_aspirations_patterns = [
        # Markdown format with **
        r"(?i)\*\*Professional\s+Aspirations\*\*:?\s*\n?\s*(.*?)(?=\*\*Skills/Interests/Hobbies\*\*|\*\*Skills/Interests\*\*|\*\*Strengths\*\*|\n\*\*|$)",
        # Without markdown, with colon
        r"(?i)Professional\s+Aspirations:?\s*\n?\s*(.*?)(?=Skills/Interests/Hobbies|Skills/Interests|Strengths|\n[A-Z]|$)",
        # Just the header word
        r"(?i)Professional\s+Aspirations\s*\n\s*(.*?)(?=Skills/Interests|Strengths|\n[A-Z]|$)",
    ]
    
    hobbies_interests_patterns = [
        # Full format with markdown
        r"(?i)\*\*Skills/Interests/Hobbies\*\*:?\s*\n?\s*(.*?)(?=\*\*Strengths\*\*|\n\*\*|$)",
        # Short format
        r"(?i)\*\*Skills/Interests\*\*:?\s*\n?\s*(.*?)(?=\*\*Strengths\*\*|\n\*\*|$)",
        # Without markdown
        r"(?i)Skills/Interests/Hobbies:?\s*\n?\s*(.*?)(?=Strengths|\n[A-Z]|$)",
        r"(?i)Skills/Interests:?\s*\n?\s*(.*?)(?=Strengths|\n[A-Z]|$)",
    ]
    
    strengths_patterns = [
        r"(?i)\*\*Strengths\*\*:?\s*\n?\s*(.*?)(?=\*\*Weaknesses\*\*|\n\*\*|$)",
        r"(?i)Strengths:?\s*\n?\s*(.*?)(?=Weaknesses|\n[A-Z]|$)",
        r"(?i)Strengths\s*\n\s*(.*?)(?=Weaknesses|\n[A-Z]|$)",
    ]
    
    weaknesses_patterns = [
        r"(?i)\*\*Weaknesses\*\*:?\s*\n?\s*(.*?)(?=\*\*Opportunities\*\*|\n\*\*|$)",
        r"(?i)Weaknesses:?\s*\n?\s*(.*?)(?=Opportunities|\n[A-Z]|$)",
        r"(?i)Weaknesses\s*\n\s*(.*?)(?=Opportunities|\n[A-Z]|$)",
    ]
    
    opportunities_patterns = [
        r"(?i)\*\*Opportunities\*\*:?\s*\n?\s*(.*?)(?=\*\*Threats\*\*|\n\*\*|$)",
        r"(?i)Opportunities:?\s*\n?\s*(.*?)(?=Threats|\n[A-Z]|$)",
        r"(?i)Opportunities\s*\n\s*(.*?)(?=Threats|\n[A-Z]|$)",
    ]
    
    threats_patterns = [
        r"(?i)\*\*Threats\*\*:?\s*\n?\s*(.*?)(?=\*\*Detailed\s+Summary\s+Analysis\*\*|\*\*Activities\*\*|Activities|Short\s+Term|Mid\s+Term|Long\s+Term|$)",
        r"(?i)Threats:?\s*\n?\s*(.*?)(?=Detailed\s+Summary\s+Analysis|Activities|Short\s+Term|Mid\s+Term|Long\s+Term|$)",
        r"(?i)Threats\s*\n\s*(.*?)(?=Detailed|Activities|Short|Mid|Long|$)",
    ]
    
    detailed_analysis_patterns = [
        r"(?i)\*\*Detailed\s+Summary\s+Analysis\*\*:?\s*\n?\s*(.*?)(?=\*\*Activities\*\*|Activities\s+to\s+Improve|Short\s+Term|Mid\s+Term|Long\s+Term|$)",
        r"(?i)Detailed\s+Summary\s+Analysis:?\s*\n?\s*(.*?)(?=Activities|Short\s+Term|Mid\s+Term|Long\s+Term|$)",
        r"(?i)Detailed\s+Summary\s+Analysis\s*\n\s*(.*?)(?=Activities|Short|Mid|Long|$)",
        r"(?i)Detailed\s+Analysis:?\s*\n?\s*(.*?)(?=Activities|Short|Mid|Long|$)",
    ]
    
    # Helper function to try multiple patterns
    def extract_section(patterns, text, section_name=""):
        for i, pattern in enumerate(patterns):
            try:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    extracted = match.group(1).strip() if match.group(1) else None
                    if extracted and len(extracted) > 10:  # Only return if we got meaningful content
                        print(f"  ✓ {section_name}: Matched pattern {i+1}, extracted {len(extracted)} chars")
                        return extracted
            except Exception as e:
                print(f"  ⚠ Pattern {i+1} for {section_name} failed: {str(e)}")
                continue
        print(f"  ✗ {section_name}: No pattern matched")
        return None
    
    # Extract fields using flexible patterns
    print(f"🔍 Attempting to extract sections...")
    professional_aspirations = extract_section(professional_aspirations_patterns, swot_analysis, "Professional Aspirations")
    hobbies_interests = extract_section(hobbies_interests_patterns, swot_analysis, "Hobbies/Interests")
    strengths = extract_section(strengths_patterns, swot_analysis, "Strengths")
    weaknesses = extract_section(weaknesses_patterns, swot_analysis, "Weaknesses")
    opportunities = extract_section(opportunities_patterns, swot_analysis, "Opportunities")
    threats = extract_section(threats_patterns, swot_analysis, "Threats")
    detailed_analysis = extract_section(detailed_analysis_patterns, swot_analysis, "Detailed Analysis")
    
    # Log extraction results for debugging
    print(f"🔍 Parsing results:")
    print(f"  Professional Aspirations: {'✓' if professional_aspirations else '✗'}")
    print(f"  Hobbies/Interests: {'✓' if hobbies_interests else '✗'}")
    print(f"  Strengths: {'✓' if strengths else '✗'}")
    print(f"  Weaknesses: {'✓' if weaknesses else '✗'}")
    print(f"  Opportunities: {'✓' if opportunities else '✗'}")
    print(f"  Threats: {'✓' if threats else '✗'}")
    print(f"  Detailed Analysis: {'✓' if detailed_analysis else '✗'}")
    
    # Function to clean the extracted text (preserve important content)
    def clean_text(text):
        if not text:
            return "Not specified"
        
        # Remove markdown bold markers but keep content
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **text** but keep text
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove *text* but keep text
        
        # Replace newlines with spaces but preserve paragraph structure
        text = text.replace('\n\n', ' PARAGRAPH_BREAK ').replace('\n', ' ')
        text = text.replace(' PARAGRAPH_BREAK ', '\n\n')
        
        # Remove excessive whitespace but keep single spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # If text is empty after cleaning, return "Not specified"
        return text if text else "Not specified"

    # Clean and return the extracted data
    result = {
        "professional_aspirations": clean_text(professional_aspirations),
        "hobbies/interests": clean_text(hobbies_interests),
        "strengths": clean_text(strengths),
        "weaknesses": clean_text(weaknesses),
        "opportunities": clean_text(opportunities),
        "threats": clean_text(threats),
        "detailed_analysis": clean_text(detailed_analysis),
    }
    
    # Log if any sections failed to parse
    failed_sections = [key for key, value in result.items() if value == "Not specified"]
    if failed_sections:
        print(f"⚠️ Warning: Failed to parse sections: {', '.join(failed_sections)}")
        print(f"📄 Full SWOT analysis text for debugging:\n{swot_analysis}")
        print(f"\n🔍 Looking for section headers in text...")
        # Try to find what headers actually exist in the text
        header_patterns = [
            r'\*\*[^*]+\*\*',
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:',
        ]
        for pattern in header_patterns:
            matches = re.findall(pattern, swot_analysis, re.MULTILINE | re.IGNORECASE)
            if matches:
                print(f"  Found headers matching pattern {pattern}: {matches[:10]}")
        
        # Try fallback: split by double newlines and look for section names
        print(f"\n🔄 Attempting fallback parsing method...")
        sections = swot_analysis.split('\n\n')
        section_map = {
            'professional': 'professional_aspirations',
            'aspirations': 'professional_aspirations',
            'skills/interests': 'hobbies/interests',
            'hobbies': 'hobbies/interests',
            'interests': 'hobbies/interests',
            'strengths': 'strengths',
            'weaknesses': 'weaknesses',
            'opportunities': 'opportunities',
            'threats': 'threats',
            'detailed': 'detailed_analysis',
            'summary': 'detailed_analysis',
        }
        
        for section_text in sections:
            section_lower = section_text.lower()
            for keyword, result_key in section_map.items():
                if keyword in section_lower and result[result_key] == "Not specified":
                    # Try to extract content after the header
                    lines = section_text.split('\n')
                    content_lines = []
                    found_header = False
                    for line in lines:
                        if keyword in line.lower() and not found_header:
                            found_header = True
                            continue
                        if found_header and line.strip():
                            content_lines.append(line.strip())
                    
                    if content_lines:
                        extracted_text = ' '.join(content_lines)
                        if len(extracted_text) > 10:
                            result[result_key] = clean_text(extracted_text)
                            print(f"  ✓ Fallback extracted {result_key} ({len(extracted_text)} chars)")
                            break
    
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
        f"Expectations when joining this college: {row['expectations']}\n"
        f"Goal Achieving Opportunities: {row['goal_achieving_opportunities']}\n"
        f"Interested in Skills Program: {row['participate_in_skill_programs']}\n"
        f"Skills Program to Participate: {row['interested_skill_programs']}\n"
        f"External Factors affecting growth: {row['external_factors_affecting_growth']}\n"
        f"Primary Stressors: {row['primary_stressors']}\n\n"
        f"Biggest Distractions: {row['biggest_distractions']}\n"
        f"Strongest Skills: {row['strongest_skills']}\n"
        f"Areas of low confidence: {row['areas_of_low_confidence']}\n"
        f"Hobbies/Interests: {row['hobbies_interests']}\n\n"
        f"1. Provide a SWOT analysis for this student in paragraph form with specific details for Strengths, Weaknesses, Opportunities, and Threats. Report should include paragraphs sections that are Professional Aspirations, Skills/Interests/Hobbies, Strengths, Weaknesses, Opportunities, Threats, and Detailed Summary Analysis and dont want points.\n"
        f"2. Based on this information, suggest 3 activities to improve this student's performance. List 3 activity per term clearly and divide it into short term (0-3 Months), mid term (3-6 Months), and long term (7-12 Months)."
        f"Use 2nd person pronoun where you are telling to me."
        f"So format should go like this for the swotanalysis."
        f"**Professional Aspirations**"
        f"Your primary goal is to become a Data Scientist at a leading tech company. This ambition is fueled by your existing skills in data analysis and programming and your experience at XYZ Corp. You recognize the need to stay current with technological advancements and are seeking opportunities to develop your skill set."
        f"**Skills/Interests/Hobbies**"
        f"You possess strong analytical and problem-solving skills coupled with good communication abilities. Your interests in data science machine learning and technology are evident through your choice of skills programs and hobbies like reading sci-fi novels and playing chess which demonstrate logical thinking abilities. Your enjoyment of music sports and spending time with family provides a balance to your academic and professional pursuits."
        f"**Strengths**"
        f"Your strengths lie in your proven analytical thinking and problem-solving skills honed through your data analyst experience at XYZ Corp. Your proficiency in mathematics programming and data analysis provides a solid foundation for your data science aspirations. You actively seek opportunities for growth demonstrated by your enthusiasm for internship programs networking events and hands-on projects."
        f"**Weaknesses**"
        f"Your weaknesses include a lack of confidence in public speaking and conflict resolution. While your data-related skills are strong you acknowledge weaknesses in History and Literature which might be less relevant to your career goals but indicate potential areas for broader personal development. Procrastination and social media distractions hinder your productivity."
        f"**Opportunities**"
        f"College offers several opportunities, including internships, networking events, and hands-on projects directly relevant to your data science aspirations. The Advanced Data Science and Machine Learning skills programs will significantly enhance your skill set.  Economic instability is a threat, but could also present opportunities to stand out if you develop highly sought-after skills.  Seeking mentorship could directly address your concerns about keeping up with technological advancements."
        f"**Threats**"
        f"Rapid advancements in technology represent a significant threat if you fail to keep up. Economic instability could limit job opportunities after graduation. Your tendency toward procrastination and social media distractions could impede your academic progress and professional development.  Lack of mentorship could hinder your growth and learning."
        f"**Detailed Summary Analysis**"
        f"* **High Potential:** You have a strong foundation in data analysis, coupled with a clear career path and proactive approach to skill development."
        f"* **Key Challenges:** Overcoming your weaknesses in public speaking, conflict resolution, and time management are crucial.  Mitigating the impact of economic instability and rapid technological change is also important."
        f"* **Strategic Focus:** Prioritize skill development in data science and machine learning, actively participate in networking opportunities, and address time management and confidence issues."
        f"**Activities**"
        f"**Short Term (0-2 Months):**"
        f"1.  **Identify and join a campus club:** Focus on a club related to data science or technology to build your network and learn from others."
        f"2.  **Enroll in a public speaking course or workshop:**  This directly addresses a key weakness."
        f"3.  **Develop a time management system:** Implement techniques like the Pomodoro Technique or time blocking to improve productivity and reduce procrastination."
        f"**Mid Term (3-6 Months):**"
        f"1.  **Actively seek mentorship:** Connect with professors, professionals in the field, or alumni working in data science."
        f"2.  **Begin applying for internships:** Target internships directly relevant to your data science aspirations."
        f"3.  **Create a professional portfolio:** Showcase your projects, skills, and experience on platforms like GitHub or LinkedIn."
        f"**Long Term (7-12 Months):**"
        f"1.  **Participate in hackathons or data science competitions:** Test your skills, learn from others, and build your portfolio."
        f"2.  **Develop a strong LinkedIn profile:** Network with professionals in your field and showcase your accomplishments."
        f"3.  **Begin researching graduate programs in data science (if applicable):** This demonstrates your long-term commitment to the field."
    )

    try:
        response = model.generate_content(prompt)
        
        if response and response.candidates:
            text_response = response.candidates[0].content.parts[0].text
            return text_response.strip() if text_response else "No analysis or suggestions available."
        else:
            return "No analysis or suggestions available."
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
