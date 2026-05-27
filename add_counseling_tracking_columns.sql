-- Add outcome and follow-up tracking columns to counseling_sessions table
-- Run this SQL to add the new tracking features

ALTER TABLE counseling_sessions ADD COLUMN IF NOT EXISTS outcome_status VARCHAR(30);
ALTER TABLE counseling_sessions ADD COLUMN IF NOT EXISTS outcome_notes TEXT;
ALTER TABLE counseling_sessions ADD COLUMN IF NOT EXISTS followup_date DATE;
ALTER TABLE counseling_sessions ADD COLUMN IF NOT EXISTS followup_scheduled BOOLEAN DEFAULT FALSE;
ALTER TABLE counseling_sessions ADD COLUMN IF NOT EXISTS parent_session_id VARCHAR(50);

-- Add index for faster lookups on parent_session_id
CREATE INDEX IF NOT EXISTS idx_counseling_parent_session ON counseling_sessions(parent_session_id);

-- Add index for followup_date queries
CREATE INDEX IF NOT EXISTS idx_counseling_followup_date ON counseling_sessions(followup_date);
