-- Mark graduated students as alumni (separate from active mentees)
ALTER TABLE students
    ADD COLUMN is_alumni BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN alumni_since DATETIME NULL;

CREATE INDEX idx_students_is_alumni ON students (is_alumni);
