-- Academic records enhancement: metadata + verification on existing marksheet tables

ALTER TABLE student_secondary_marksheets
    ADD COLUMN document_type VARCHAR(20) NULL,
    ADD COLUMN board_university VARCHAR(255) NULL,
    ADD COLUMN institution_name VARCHAR(255) NULL,
    ADD COLUMN year_of_passing VARCHAR(20) NULL,
    ADD COLUMN percentage_cgpa VARCHAR(50) NULL,
    ADD COLUMN verification_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    ADD COLUMN remarks TEXT NULL,
    ADD COLUMN uploaded_by VARCHAR(255) NULL,
    ADD COLUMN verified_by VARCHAR(255) NULL,
    ADD COLUMN verified_at DATETIME NULL,
    ADD COLUMN file_hash VARCHAR(64) NULL;

CREATE INDEX idx_ssm_usn_status ON student_secondary_marksheets (student_usn, verification_status);
CREATE INDEX idx_ssm_year ON student_secondary_marksheets (year_of_passing);

UPDATE student_secondary_marksheets SET document_type = '10th' WHERE standard = 10 AND (document_type IS NULL OR document_type = '');
UPDATE student_secondary_marksheets SET document_type = '12th' WHERE standard = 12 AND (document_type IS NULL OR document_type = '');

ALTER TABLE academic_performance_marksheets
    ADD COLUMN sgpa VARCHAR(20) NULL,
    ADD COLUMN cgpa VARCHAR(20) NULL,
    ADD COLUMN percentage VARCHAR(20) NULL,
    ADD COLUMN total_credits VARCHAR(20) NULL,
    ADD COLUMN backlogs VARCHAR(100) NULL,
    ADD COLUMN result_status VARCHAR(50) NULL,
    ADD COLUMN academic_year VARCHAR(32) NULL,
    ADD COLUMN verification_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    ADD COLUMN remarks TEXT NULL,
    ADD COLUMN uploaded_by VARCHAR(255) NULL,
    ADD COLUMN verified_by VARCHAR(255) NULL,
    ADD COLUMN verified_at DATETIME NULL,
    ADD COLUMN file_hash VARCHAR(64) NULL;

CREATE INDEX idx_apm_usn_status ON academic_performance_marksheets (student_usn, verification_status);
CREATE INDEX idx_apm_usn_semester ON academic_performance_marksheets (student_usn, semester);
