-- Create email_logs table for tracking sent emails
CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id VARCHAR(255) NOT NULL,
    student_usn VARCHAR(255),
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'sent',
    email_type VARCHAR(100) DEFAULT 'manual',
    FOREIGN KEY (mentor_id) REFERENCES mentors(mentor_id) ON DELETE CASCADE,
    FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE SET NULL,
    INDEX idx_mentor_id (mentor_id),
    INDEX idx_sent_at (sent_at)
);

-- Add comment
ALTER TABLE email_logs COMMENT = 'Stores history of emails sent by mentors to students';
