-- Add column for student support feedback file (S3 key) so mentee can upload and mentor can view.
-- Run this once against your database. If you get "column already exists", you can ignore it.

ALTER TABLE counseling_sessions
ADD COLUMN student_feedback_file VARCHAR(500) NULL;
