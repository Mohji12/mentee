-- Add referral columns to counseling_sessions (MySQL)
ALTER TABLE counseling_sessions ADD COLUMN referred_to_name VARCHAR(255) NULL;
ALTER TABLE counseling_sessions ADD COLUMN referred_to_contact VARCHAR(100) NULL;
ALTER TABLE counseling_sessions ADD COLUMN referred_at DATETIME NULL;

-- Create session_issues_resolutions table (Details of Issues Raised & Resolved)
CREATE TABLE IF NOT EXISTS session_issues_resolutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    counseling_id VARCHAR(50) NOT NULL,
    serial_no INT NOT NULL,
    issues_raised TEXT NOT NULL,
    date_issue_raised DATE NOT NULL,
    resolution_details TEXT NOT NULL,
    date_resolution_provided DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (counseling_id) REFERENCES counseling_sessions(counseling_id) ON DELETE CASCADE,
    INDEX idx_counseling_id (counseling_id)
);
