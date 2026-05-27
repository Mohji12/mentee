-- Tabular feedback on session card: Issue Raised by Mentor, Details of Resolution, Resolution (description, date, status).
CREATE TABLE IF NOT EXISTS counseling_issue_resolution_feedback (
    id SERIAL PRIMARY KEY,
    counseling_id VARCHAR(50) NOT NULL REFERENCES counseling_sessions(counseling_id) ON DELETE CASCADE,
    row_type VARCHAR(30) NOT NULL,
    description TEXT,
    feedback_date DATE,
    status VARCHAR(10),
    UNIQUE(counseling_id, row_type)
);

CREATE INDEX IF NOT EXISTS ix_counseling_issue_resolution_feedback_counseling_id ON counseling_issue_resolution_feedback(counseling_id);
