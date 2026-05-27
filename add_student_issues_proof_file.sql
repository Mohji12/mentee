-- Add column for mentee's proof of work done after session (Issues & Resolution form).
-- Run if counseling_sessions already exists.

ALTER TABLE counseling_sessions ADD COLUMN student_issues_proof_file VARCHAR(500) NULL;
