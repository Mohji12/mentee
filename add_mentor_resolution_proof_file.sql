-- Mentor can upload a resolution proof (e.g. PDF) in the Issues & Resolution section.
ALTER TABLE counseling_sessions ADD COLUMN mentor_resolution_proof_file VARCHAR(500) NULL;
