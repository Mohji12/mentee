-- Add is_locked column to existing academic_performance table
-- Run this if you already have the academic_performance table

ALTER TABLE academic_performance ADD COLUMN is_locked BOOLEAN DEFAULT FALSE NOT NULL;
