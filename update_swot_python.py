"""
Python script to update SWOT analysis in the database
This script handles the update more safely than raw SQL
"""
import pymysql
from app.db.database import DATABASE_URL
import re

# Parse database URL
# Format: mysql+pymysql://user:password@host:port/database
url_match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
if not url_match:
    print("Error: Could not parse DATABASE_URL")
    exit(1)

user, password, host, port, database = url_match.groups()

# SWOT analysis text
swot_text = """## SWOT Analysis for Aspiring Data Scientist

**Professional Aspirations:** The student aims to become a Data Scientist, driven by a strong interest in machine learning.  Their fresher status presents a challenge, but their aspiration aligns well with their declared strength in machine learning.  A significant gap exists in their mathematical foundation, which is crucial for success in data science.  Overcoming this fear of not achieving their goal is paramount.

**Skills/Interests/Hobbies:** The student's strength in convincing people is a valuable soft skill applicable to client presentations and teamwork in data science.  Their interest in playing cricket demonstrates discipline and teamwork – transferable skills beneficial in collaborative projects.  Coding skills, actively pursued through the Skills Program, will be vital.

**Strengths:**

* **Machine Learning Proficiency:**  A strong foundation in machine learning provides a crucial advantage in the data science field. This is a significant asset that should be further developed.
* **Persuasive Communication:** The ability to convince people is a highly valued soft skill in data science, essential for presenting findings and collaborating effectively.
* **Goal-Oriented:**  The student's clear professional dream and identification of happiness sources linked to achievements showcase a strong work ethic and motivation.
* **Resourcefulness (implied):** Seeking out skills programs like coding indicates a proactive approach to addressing their skill gaps.


**Weaknesses:**

* **Mathematics Weakness:** This is a significant weakness, as a solid mathematical foundation (linear algebra, calculus, statistics) is indispensable for understanding and applying many data science techniques.  Without addressing this, their machine learning skills will be limited.
* **Communication Confidence:**  While possessing persuasive skills, a lack of confidence in general communication could hinder networking, presentations, and team interactions.
* **Distraction from Social Media:** Excessive social media usage can severely impact study time and productivity, hindering progress toward their goals.
* **Prone to Hyperactivity:** This may lead to decreased focus and reduced ability to manage workloads efficiently, impacting both academic and professional pursuits.


**Opportunities:**

* **Jain University Resources:** Leverage the university's resources, including academic advising, tutoring services (potentially for math), workshops, and networking events with industry professionals.
* **Skills Program Participation:** The coding skills program offers a direct path to improving a key data science skill.  Explore additional courses or workshops offered by the university or online platforms like Coursera or edX to enhance their programming skills.
* **Internships:** Seek internships at data-driven companies to gain practical experience and build their resume. Platforms like LinkedIn and Indeed are valuable resources for finding internships.
* **Networking:** Actively network with professors, alumni, and professionals in the data science field through university events, online communities (like LinkedIn groups), and industry meetups.


**Threats:**

* **Financial Issues:**  Financial constraints could limit access to crucial resources like tutoring, software, or even higher education opportunities.
* **Competition:** The data science field is highly competitive.  The student needs to differentiate themselves through strong skills, impactful projects, and effective networking.
* **Rapid Technological Advancements:** The data science field is constantly evolving. Continuous learning and adaptation are vital to remain competitive.
* **Lack of Mentorship:**  Without guidance from experienced professionals, it might be difficult to navigate the complexities of the field and tailor their skills effectively.


**Detailed Summary Analysis:** This student possesses significant potential in data science, fueled by their strong interest in machine learning and a determined attitude. However, their mathematical weakness poses a substantial hurdle.  Addressing this weakness is crucial, as it underpins the entire field. Simultaneously, improving communication confidence and managing distractions are essential for maximizing their academic and professional performance.  Leveraging Jain University's resources and actively seeking internships and networking opportunities will significantly enhance their chances of success.  Mitigating financial challenges and proactively adapting to technological advancements will be vital for long-term success.  Finding a mentor in the field can provide invaluable guidance and support.


## Activities

**Short Term (0-2 Months):**

1. **Strengthen Math Foundations:** Enroll in a basic mathematics course or online tutorials focusing on algebra, calculus, and statistics.  Utilize Khan Academy for free resources, Coursera or edX for structured courses, and seek tutoring services from the university or local learning centers.
2. **Improve Time Management & Focus:** Implement techniques like the Pomodoro Technique to improve focus and reduce social media distractions. Use productivity apps like Forest or Freedom to limit social media access during study time. Join a university-sponsored study group for peer support and accountability.
3. **Begin Networking:** Attend university information sessions and career fairs to connect with professionals in the data science field. Start building a professional LinkedIn profile, highlighting their machine learning skills and career aspirations.


**Mid Term (3-6 Months):**

1. **Intermediate Coding Projects:** Complete several coding projects on platforms like HackerRank or LeetCode, focusing on data manipulation and analysis using Python or R. Participate in coding challenges and hackathons organized by the university or online coding communities.  Attend workshops offered by platforms like DataCamp or Udacity.
2. **Seek Mentorship:** Connect with data science professors at the university or reach out to professionals through LinkedIn to explore mentorship opportunities. Many universities have alumni networks that can facilitate introductions.
3. **Develop a Portfolio:** Create a portfolio showcasing their completed projects, highlighting their skills and achievements.  GitHub is an excellent platform for sharing code and projects, and it also assists in networking.


**Long Term (7-12 Months):**

1. **Advanced Data Science Projects:** Undertake more complex data science projects, potentially involving machine learning models and data visualization. Consider participating in research projects or contributing to open-source projects. Utilize Kaggle to find datasets and participate in competitions.
2. **Internship & Job Search:** Secure a relevant internship in data science to gain practical experience and build their resume. Actively search for entry-level data scientist positions using platforms like LinkedIn, Indeed, and Glassdoor.  Network with recruiters attending university career events.
3. **Advanced Skill Development:** Pursue advanced certifications in data science (e.g., Google Data Analytics Professional Certificate, AWS Certified Machine Learning – Specialty) to demonstrate expertise to potential employers. Continue learning through online courses, conferences, and workshops."""

student_usn = '23MSRDS018'

try:
    # Connect to database
    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        # Step 1: Check column type and alter if needed
        cursor.execute("""
            SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'swot' 
            AND COLUMN_NAME = 'swot_analysis'
        """, (database,))
        
        result = cursor.fetchone()
        if result:
            data_type, max_length = result
            print(f"Current column type: {data_type}({max_length})")
            
            if data_type != 'text' and data_type != 'longtext':
                print("Altering column type to TEXT...")
                cursor.execute("ALTER TABLE swot MODIFY COLUMN swot_analysis TEXT")
                connection.commit()
                print("Column type updated successfully!")
        
        # Step 2: Check if record exists
        cursor.execute("SELECT id FROM swot WHERE student_usn = %s", (student_usn,))
        existing = cursor.fetchone()
        
        if existing:
            # Step 3: Update existing record
            print(f"Updating existing record for student {student_usn}...")
            cursor.execute(
                "UPDATE swot SET swot_analysis = %s WHERE student_usn = %s",
                (swot_text, student_usn)
            )
            connection.commit()
            print("Update successful!")
        else:
            # Step 4: Insert new record
            print(f"Inserting new record for student {student_usn}...")
            cursor.execute(
                "INSERT INTO swot (student_usn, swot_analysis) VALUES (%s, %s)",
                (student_usn, swot_text)
            )
            connection.commit()
            print("Insert successful!")
        
        # Step 5: Verify
        cursor.execute(
            "SELECT LENGTH(swot_analysis) as text_length FROM swot WHERE student_usn = %s",
            (student_usn,)
        )
        result = cursor.fetchone()
        if result:
            print(f"Verified: SWOT analysis text length = {result[0]} characters")
    
    connection.close()
    print("Done!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()





