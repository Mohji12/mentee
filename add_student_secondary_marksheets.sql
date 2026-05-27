-- Table for 10th and 12th standard marksheets (prerequisite before semester grades)
-- Run this migration to add the student_secondary_marksheets table.

CREATE TABLE IF NOT EXISTS student_secondary_marksheets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_usn VARCHAR(255) NOT NULL,
    standard INT NOT NULL COMMENT '10 or 12',
    marksheet_url VARCHAR(500) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_secondary_marksheet_student FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    CONSTRAINT uq_student_secondary_standard UNIQUE (student_usn, standard)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
