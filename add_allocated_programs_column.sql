-- Add allocated_programs column to committee_members table
-- Run this SQL script on your database before using the program faculty feature

ALTER TABLE committee_members 
ADD COLUMN allocated_programs TEXT NULL COMMENT 'JSON array as string for program_faculty only';
