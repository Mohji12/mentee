-- Academic performance: no ALTER on students; use lock table instead (MySQL)

-- Create academic_performance table
CREATE TABLE IF NOT EXISTS academic_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_usn VARCHAR(255) NOT NULL,
    semester INT NOT NULL,
    course VARCHAR(255) NOT NULL,
    grade VARCHAR(50) NULL,
    overall_attendance VARCHAR(50) NULL,
    is_locked BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    INDEX idx_student_semester (student_usn, semester)
);

-- Add is_locked column if table already exists (run this if you already have academic_performance table)
-- ALTER TABLE academic_performance ADD COLUMN is_locked BOOLEAN DEFAULT FALSE NOT NULL;

-- Lock table: one row per student when they submit (one-time submit)
CREATE TABLE IF NOT EXISTS academic_performance_lock (
    student_usn VARCHAR(255) NOT NULL PRIMARY KEY,
    submitted_at DATETIME NOT NULL,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
);
