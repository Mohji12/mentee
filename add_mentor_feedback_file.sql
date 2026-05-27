-- Add mentor_feedback_file column for mentor's feedback proof (PDF).
-- Run once. If column already exists, ignore the error.

ALTER TABLE counseling_sessions
ADD COLUMN mentor_feedback_file VARCHAR(500) NULL;
