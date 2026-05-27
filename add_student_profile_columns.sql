-- Add gender, blood_group, date_of_birth, parent_guardian_contact to students table (MySQL)
-- Run this once against your database. If you get "Duplicate column" errors, the columns already exist.

ALTER TABLE students ADD COLUMN gender VARCHAR(20) NULL;
ALTER TABLE students ADD COLUMN blood_group VARCHAR(10) NULL;
ALTER TABLE students ADD COLUMN date_of_birth DATE NULL;
ALTER TABLE students ADD COLUMN parent_guardian_contact VARCHAR(20) NULL;
