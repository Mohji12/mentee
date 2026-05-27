-- Create pf16_responses table for 16PF form submissions
CREATE TABLE IF NOT EXISTS pf16_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_usn VARCHAR(255) NOT NULL,
    responses TEXT NOT NULL COMMENT 'JSON string with question-answer pairs: {"1": "a", "2": "b", ...}',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_student_usn (student_usn),
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE
);
