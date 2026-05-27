-- =====================================================
-- MySQL CREATE TABLE Statements for Attendance Models
-- =====================================================

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Attendance Sessions Table
DROP TABLE IF EXISTS attendance_sessions;
CREATE TABLE attendance_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    mentor_id VARCHAR(255) NOT NULL,
    session_name VARCHAR(255),
    qr_code_data TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    location VARCHAR(255),
    CONSTRAINT fk_attendance_sessions_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Attendance Table
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    mentor_id VARCHAR(255) NOT NULL,
    marked_at DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'present',
    notes TEXT,
    CONSTRAINT fk_attendance_session FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    CONSTRAINT fk_attendance_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_session (student_usn, session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create indexes for better performance
CREATE INDEX idx_attendance_sessions_mentor ON attendance_sessions(mentor_id);
CREATE INDEX idx_attendance_sessions_active ON attendance_sessions(is_active, expires_at);
CREATE INDEX idx_attendance_student ON attendance(student_usn);
CREATE INDEX idx_attendance_session ON attendance(session_id);
CREATE INDEX idx_attendance_mentor ON attendance(mentor_id);




