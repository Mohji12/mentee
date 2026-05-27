-- Add mother/father contact columns to students table
-- Run this once against your database.

ALTER TABLE students
  ADD COLUMN IF NOT EXISTS mother_contact VARCHAR(20);

ALTER TABLE students
  ADD COLUMN IF NOT EXISTS father_contact VARCHAR(20);

