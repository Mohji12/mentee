-- =====================================================
-- SQL CREATE TABLE Statements for All Models
-- Generated from app/db/models/
-- =====================================================

-- 1. Admin Table
CREATE TABLE IF NOT EXISTS admin (
    admin_id VARCHAR(255) PRIMARY KEY,
    admin_name VARCHAR(255) NOT NULL,
    admin_department VARCHAR(255) NOT NULL,
    admin_campus VARCHAR(255) NOT NULL,
    admin_email VARCHAR(255) UNIQUE NOT NULL,
    admin_phoneno VARCHAR(255) NOT NULL,
    admin_password VARCHAR(255) NOT NULL
);

-- 2. Mentors Table
CREATE TABLE IF NOT EXISTS mentors (
    mentor_id VARCHAR(255) PRIMARY KEY,
    mentor_name VARCHAR(255) NOT NULL,
    mentor_department VARCHAR(255) NOT NULL,
    mentor_email VARCHAR(255) UNIQUE NOT NULL,
    mentor_phoneno VARCHAR(255) NOT NULL,
    mentor_password VARCHAR(255) NOT NULL
);

-- 3. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_usn VARCHAR(255) PRIMARY KEY,
    student_name VARCHAR(255),
    student_email VARCHAR(255) UNIQUE NOT NULL,
    student_phoneno VARCHAR(255),
    student_program VARCHAR(255),
    semester INT,
    student_batch VARCHAR(255),
    assigned_mentor VARCHAR(255),
    student_password VARCHAR(255) NOT NULL,
    linkedin VARCHAR(255),
    FOREIGN KEY (assigned_mentor) REFERENCES mentors(mentor_id)
);

-- 4. Activities Table
CREATE TABLE IF NOT EXISTS activities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(20),
    short_term VARCHAR(255),
    short_term1 VARCHAR(255),
    short_term2 VARCHAR(255),
    mid_term VARCHAR(255),
    mid_term1 VARCHAR(255),
    mid_term2 VARCHAR(255),
    long_term VARCHAR(255),
    long_term1 VARCHAR(255),
    long_term2 VARCHAR(255),
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn)
);

-- 5. Activities Tracking Table
CREATE TABLE IF NOT EXISTS activities_tracking (
    id VARCHAR(255) PRIMARY KEY,
    student_usn VARCHAR(255),
    activities VARCHAR(255),
    duration_type VARCHAR(255),
    deadline DATETIME,
    remarks VARCHAR(255),
    completed_in INT,
    benefitted BOOLEAN DEFAULT FALSE,
    rejection_reason TEXT,
    proof VARCHAR(255),
    status VARCHAR(255) DEFAULT 'Pending',
    percentage INT,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn)
);

-- 6. Activity Submissions Table
CREATE TABLE IF NOT EXISTS activity_submissions (
    submission_id VARCHAR(20) PRIMARY KEY,
    activity_id VARCHAR(20) NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    mentor_id VARCHAR(255) NOT NULL,
    proof VARCHAR(2048) NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',
    rejection_reason TEXT,
    completed_in INT,
    percentage INT,
    FOREIGN KEY (activity_id) REFERENCES activities_tracking(id),
    FOREIGN KEY (student_usn) REFERENCES students(student_usn),
    FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id)
);

-- 7. Counseling Sessions Table
CREATE TABLE IF NOT EXISTS counseling_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    counseling_id VARCHAR(50) UNIQUE NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    mentor_id VARCHAR(255) NOT NULL,
    session_date DATETIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    google_meet_link VARCHAR(500),
    meeting_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT,
    feedback TEXT,
    is_urgent BOOLEAN DEFAULT FALSE,
    student_feedback TEXT,
    student_rating INT,
    student_feedback_date DATETIME,
    mentor_feedback TEXT,
    mentor_rating INT,
    mentor_feedback_date DATETIME,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn),
    FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id),
    INDEX idx_counseling_id (counseling_id)
);

-- 8. Counseling Availability Table
CREATE TABLE IF NOT EXISTS counseling_availability (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id VARCHAR(255) NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time VARCHAR(10) NOT NULL,
    end_time VARCHAR(10) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    available_from DATETIME,
    available_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id),
    INDEX idx_mentor_id (mentor_id)
);

-- 9. Competencies Table
CREATE TABLE IF NOT EXISTS competencies (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(20) NOT NULL,
    Active_Listening INT CHECK (Active_Listening BETWEEN 0 AND 35),
    Building_Trust INT CHECK (Building_Trust BETWEEN 0 AND 35),
    Encouraging INT CHECK (Encouraging BETWEEN 0 AND 35),
    Identifying_Goals_Current_Reality INT CHECK (Identifying_Goals_Current_Reality BETWEEN 0 AND 35),
    Instructing_Developing_Capabilities INT CHECK (Instructing_Developing_Capabilities BETWEEN 0 AND 35),
    Inspiring INT CHECK (Inspiring BETWEEN 0 AND 35),
    Providing_Corrective_Feedback INT CHECK (Providing_Corrective_Feedback BETWEEN 0 AND 35),
    Managing_Risks INT CHECK (Managing_Risks BETWEEN 0 AND 35),
    Opening_Doors INT CHECK (Opening_Doors BETWEEN 0 AND 35),
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
);

-- 10. Mentoring Assessments Table (MCA Assignments)
CREATE TABLE IF NOT EXISTS mentoring_assessments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    -- Page 1 (8 questions)
    listens_carefully INT,
    discouraged_by_criticism INT,
    builds_trust INT,
    adapts_to_styles INT,
    shares_with_classmates INT,
    sets_expectations INT,
    aligns_expectations INT,
    wants_mentor_to_adapt INT,
    -- Page 2 (8 questions)
    expects_improvement_feedback INT,
    understands_diff_impacts INT,
    goal_setting_with_mentor INT,
    sees_mentor_as_role_model INT,
    aligns_with_industry_expectations INT,
    polite_repetition_reminder INT,
    estimates_mentor_knowledge INT,
    considers_industry_exposure INT,
    -- Page 3 (8 questions)
    self_assess_abilities INT,
    understands_worklife_balance INT,
    discusses_knowledge_strategies INT,
    avoids_using_mentor_network INT,
    discusses_goal_strategies INT,
    improves_communication INT,
    stays_self_motivated INT,
    discusses_career_options INT,
    -- Page 4 (8 questions)
    frequent_meetings INT,
    extra_effort_due_to_exposure INT,
    prefers_active_sessions INT,
    seeks_networking_support INT,
    wants_showcasing_contributions INT,
    handles_background_differences INT,
    expects_independence INT,
    wants_feedback_grouped INT,
    -- Page 5 (8 questions)
    avoids_bias_prejudice INT,
    expects_motivation_support INT,
    works_with_diverse_mentors INT,
    likes_success_stories INT,
    expects_networking_help INT,
    encouraged_for_projects INT,
    expects_career_exposure INT,
    supports_experimentation INT,
    -- Page 6 (5 questions)
    supports_industry_interaction INT,
    respects_contrary_views INT,
    encourages_market_analysis INT,
    showcases_contributions INT,
    accepts_open_criticism INT,
    -- Timestamp
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_student_usn (student_usn)
);

-- 11. Query Table
CREATE TABLE IF NOT EXISTS query (
    id VARCHAR(50) PRIMARY KEY,
    usn VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    phoneno VARCHAR(15),
    program VARCHAR(255),
    ass_mentor VARCHAR(255),
    query_issue TEXT,
    FOREIGN KEY (usn) REFERENCES students(student_usn) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 12. Psychometric Responses Table
CREATE TABLE IF NOT EXISTS psychometric_responses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    present_address TEXT,
    permanent_address TEXT,
    educational_qualifications TEXT,
    subjects_strength TEXT,
    subjects_weakness TEXT,
    previous_work_experience TEXT,
    father_name VARCHAR(255),
    father_mobile_no VARCHAR(255),
    father_education VARCHAR(255),
    father_employment VARCHAR(255),
    mother_name VARCHAR(255),
    mother_mobile_no VARCHAR(255),
    mother_education VARCHAR(255),
    mother_employment VARCHAR(255),
    siblings_details TEXT,
    professional_dream TEXT,
    professional_fear TEXT,
    happiness_sources TEXT,
    expectations TEXT,
    goal_achieving_opportunities TEXT,
    participate_in_skill_programs TEXT,
    interested_skill_programs TEXT,
    external_factors_affecting_growth TEXT,
    primary_stressors TEXT,
    biggest_distractions TEXT,
    strongest_skills TEXT,
    areas_of_low_confidence TEXT,
    hobbies_interests TEXT,
    consent_given VARCHAR(255),
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_id (id)
);

-- 13. SWOT Table
CREATE TABLE IF NOT EXISTS swot (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255),
    swot_analysis TEXT,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn),
    INDEX idx_student_usn (student_usn),
    INDEX idx_id (id)
);

-- 14. Report Table
CREATE TABLE IF NOT EXISTS report (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(20) NOT NULL,
    professional_aspirations TEXT NOT NULL,
    hobbies_interests TEXT NOT NULL,
    strengths TEXT NOT NULL,
    weaknesses TEXT NOT NULL,
    opportunities TEXT NOT NULL,
    threats TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn),
    INDEX idx_id (id)
);

-- 15. Mentee Competency Report Table
CREATE TABLE IF NOT EXISTS mentee_competency_report (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    competency VARCHAR(255) NOT NULL,
    observation TEXT,
    mentor_implication TEXT,
    recommendation TEXT,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
);

-- 16. Meetings Table
CREATE TABLE IF NOT EXISTS meetings (
    srno INT PRIMARY KEY AUTO_INCREMENT,
    id VARCHAR(36),
    mentor_id VARCHAR(50) NOT NULL,
    student_usn VARCHAR(50) NOT NULL,
    meeting_date DATETIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    progress_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    attendance VARCHAR(50),
    agenda VARCHAR(255),
    duration INT,
    FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id),
    FOREIGN KEY (student_usn) REFERENCES students(student_usn),
    INDEX idx_id (id)
);

-- 17. Login Table
CREATE TABLE IF NOT EXISTS login (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ms_ids VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exp_timestamp DATETIME NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    jti VARCHAR(255) NOT NULL
);

-- 18. Forgot Password Table
CREATE TABLE IF NOT EXISTS forgot_password (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_student_id VARCHAR(255),
    email_id VARCHAR(255) NOT NULL,
    otp_code VARCHAR(255) NOT NULL,
    INDEX idx_mentor_student_id (mentor_student_id),
    INDEX idx_id (id)
);

-- =====================================================
-- Summary: 18 Tables Created
-- =====================================================
-- 1. admin
-- 2. mentors
-- 3. students
-- 4. activities
-- 5. activities_tracking
-- 6. activity_submissions
-- 7. counseling_sessions
-- 8. counseling_availability
-- 9. competencies
-- 10. mentoring_assessments
-- 11. query
-- 12. psychometric_responses
-- 13. swot
-- 14. report
-- 15. mentee_competency_report
-- 16. meetings
-- 17. login
-- 18. forgot_password
-- =====================================================





