-- =====================================================
-- MySQL CREATE TABLE Statements for All Models
-- Generated from app/db/models/
-- =====================================================
-- IMPORTANT: Run this script in MySQL Workbench SQL Editor, NOT the Import Wizard
-- =====================================================

-- Disable foreign key checks temporarily to avoid dependency issues
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Admin Table
DROP TABLE IF EXISTS admin;
CREATE TABLE admin (
    admin_id VARCHAR(255) PRIMARY KEY,
    admin_name VARCHAR(255) NOT NULL,
    admin_department VARCHAR(255) NOT NULL,
    admin_campus VARCHAR(255) NOT NULL,
    admin_email VARCHAR(255) UNIQUE NOT NULL,
    admin_phoneno VARCHAR(255) NOT NULL,
    admin_password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Mentors Table
DROP TABLE IF EXISTS mentors;
CREATE TABLE mentors (
    mentor_id VARCHAR(255) PRIMARY KEY,
    mentor_name VARCHAR(255) NOT NULL,
    mentor_department VARCHAR(255) NOT NULL,
    mentor_email VARCHAR(255) UNIQUE NOT NULL,
    mentor_phoneno VARCHAR(255) NOT NULL,
    mentor_password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Students Table
DROP TABLE IF EXISTS students;
CREATE TABLE students (
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
    CONSTRAINT fk_students_mentor FOREIGN KEY (assigned_mentor) REFERENCES mentors(mentor_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3.1 Experience Learning Table
DROP TABLE IF EXISTS experience_learning;
CREATE TABLE experience_learning (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    detailed_explanation TEXT NOT NULL,
    proof_file_path VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_experience_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_experience_student_usn (student_usn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Activities Table
DROP TABLE IF EXISTS activities;
CREATE TABLE activities (
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
    CONSTRAINT fk_activities_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Activities Tracking Table
DROP TABLE IF EXISTS activities_tracking;
CREATE TABLE activities_tracking (
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
    CONSTRAINT fk_activities_tracking_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Activity Submissions Table
DROP TABLE IF EXISTS activity_submissions;
CREATE TABLE activity_submissions (
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
    CONSTRAINT fk_submissions_activity FOREIGN KEY (activity_id) REFERENCES activities_tracking(id) ON DELETE CASCADE,
    CONSTRAINT fk_submissions_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    CONSTRAINT fk_submissions_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Counseling Sessions Table
DROP TABLE IF EXISTS counseling_sessions;
CREATE TABLE counseling_sessions (
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
    CONSTRAINT fk_counseling_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    CONSTRAINT fk_counseling_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE,
    INDEX idx_counseling_id (counseling_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Counseling Availability Table
DROP TABLE IF EXISTS counseling_availability;
CREATE TABLE counseling_availability (
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
    CONSTRAINT fk_availability_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE,
    INDEX idx_availability_mentor (mentor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Competencies Table
DROP TABLE IF EXISTS competencies;
CREATE TABLE competencies (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(20) NOT NULL,
    Active_Listening INT,
    Building_Trust INT,
    Encouraging INT,
    Identifying_Goals_Current_Reality INT,
    Instructing_Developing_Capabilities INT,
    Inspiring INT,
    Providing_Corrective_Feedback INT,
    Managing_Risks INT,
    Opening_Doors INT,
    CONSTRAINT chk_active_listening CHECK (Active_Listening IS NULL OR Active_Listening BETWEEN 0 AND 35),
    CONSTRAINT chk_building_trust CHECK (Building_Trust IS NULL OR Building_Trust BETWEEN 0 AND 35),
    CONSTRAINT chk_encouraging CHECK (Encouraging IS NULL OR Encouraging BETWEEN 0 AND 35),
    CONSTRAINT chk_identifying_goals CHECK (Identifying_Goals_Current_Reality IS NULL OR Identifying_Goals_Current_Reality BETWEEN 0 AND 35),
    CONSTRAINT chk_instructing CHECK (Instructing_Developing_Capabilities IS NULL OR Instructing_Developing_Capabilities BETWEEN 0 AND 35),
    CONSTRAINT chk_inspiring CHECK (Inspiring IS NULL OR Inspiring BETWEEN 0 AND 35),
    CONSTRAINT chk_feedback CHECK (Providing_Corrective_Feedback IS NULL OR Providing_Corrective_Feedback BETWEEN 0 AND 35),
    CONSTRAINT chk_risks CHECK (Managing_Risks IS NULL OR Managing_Risks BETWEEN 0 AND 35),
    CONSTRAINT chk_doors CHECK (Opening_Doors IS NULL OR Opening_Doors BETWEEN 0 AND 35),
    CONSTRAINT fk_competencies_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Mentoring Assessments Table (MCA Assignments)
DROP TABLE IF EXISTS mentoring_assessments;
CREATE TABLE mentoring_assessments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    listens_carefully INT,
    discouraged_by_criticism INT,
    builds_trust INT,
    adapts_to_styles INT,
    shares_with_classmates INT,
    sets_expectations INT,
    aligns_expectations INT,
    wants_mentor_to_adapt INT,
    expects_improvement_feedback INT,
    understands_diff_impacts INT,
    goal_setting_with_mentor INT,
    sees_mentor_as_role_model INT,
    aligns_with_industry_expectations INT,
    polite_repetition_reminder INT,
    estimates_mentor_knowledge INT,
    considers_industry_exposure INT,
    self_assess_abilities INT,
    understands_worklife_balance INT,
    discusses_knowledge_strategies INT,
    avoids_using_mentor_network INT,
    discusses_goal_strategies INT,
    improves_communication INT,
    stays_self_motivated INT,
    discusses_career_options INT,
    frequent_meetings INT,
    extra_effort_due_to_exposure INT,
    prefers_active_sessions INT,
    seeks_networking_support INT,
    wants_showcasing_contributions INT,
    handles_background_differences INT,
    expects_independence INT,
    wants_feedback_grouped INT,
    avoids_bias_prejudice INT,
    expects_motivation_support INT,
    works_with_diverse_mentors INT,
    likes_success_stories INT,
    expects_networking_help INT,
    encouraged_for_projects INT,
    expects_career_exposure INT,
    supports_experimentation INT,
    supports_industry_interaction INT,
    respects_contrary_views INT,
    encourages_market_analysis INT,
    showcases_contributions INT,
    accepts_open_criticism INT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assessments_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_assessments_student (student_usn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Query Table
DROP TABLE IF EXISTS query;
CREATE TABLE query (
    id VARCHAR(50) PRIMARY KEY,
    usn VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    phoneno VARCHAR(15),
    program VARCHAR(255),
    ass_mentor VARCHAR(255),
    query_issue TEXT,
    CONSTRAINT fk_query_student FOREIGN KEY (usn) REFERENCES students(student_usn) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Psychometric Responses Table
DROP TABLE IF EXISTS psychometric_responses;
CREATE TABLE psychometric_responses (
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
    INDEX idx_psychometric_id (id),
    INDEX idx_psychometric_usn (student_usn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. SWOT Table
DROP TABLE IF EXISTS swot;
CREATE TABLE swot (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255),
    swot_analysis TEXT,
    CONSTRAINT fk_swot_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_swot_student (student_usn),
    INDEX idx_swot_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. Report Table
DROP TABLE IF EXISTS report;
CREATE TABLE report (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(20) NOT NULL,
    professional_aspirations TEXT NOT NULL,
    hobbies_interests TEXT NOT NULL,
    strengths TEXT NOT NULL,
    weaknesses TEXT NOT NULL,
    opportunities TEXT NOT NULL,
    threats TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    CONSTRAINT fk_report_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_report_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. Mentee Competency Report Table
DROP TABLE IF EXISTS mentee_competency_report;
CREATE TABLE mentee_competency_report (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_usn VARCHAR(255) NOT NULL,
    competency VARCHAR(255) NOT NULL,
    observation TEXT,
    mentor_implication TEXT,
    recommendation TEXT,
    CONSTRAINT fk_competency_report_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 16. Meetings Table
DROP TABLE IF EXISTS meetings;
CREATE TABLE meetings (
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
    meeting_mode VARCHAR(20) DEFAULT 'offline',
    google_meet_link VARCHAR(500) NULL,
    CONSTRAINT fk_meetings_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE,
    CONSTRAINT fk_meetings_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_meetings_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 17. Login Table
DROP TABLE IF EXISTS login;
CREATE TABLE login (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ms_ids VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exp_timestamp DATETIME NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    jti VARCHAR(255) NOT NULL,
    INDEX idx_login_ms_ids (ms_ids)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 18. Forgot Password Table
DROP TABLE IF EXISTS forgot_password;
CREATE TABLE forgot_password (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_student_id VARCHAR(255),
    email_id VARCHAR(255) NOT NULL,
    otp_code VARCHAR(255) NOT NULL,
    INDEX idx_forgot_mentor_student (mentor_student_id),
    INDEX idx_forgot_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

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





