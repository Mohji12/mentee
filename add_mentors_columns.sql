-- =====================================================
-- ALTER TABLE Commands to Add Columns to mentors Table
-- =====================================================

-- Add designation column
ALTER TABLE mentors 
ADD COLUMN designation VARCHAR(255) AFTER mentor_department;

-- Add profile_picture column
ALTER TABLE mentors 
ADD COLUMN profile_picture VARCHAR(500) AFTER designation;

-- =====================================================
-- Alternative: Add both columns in one command
-- =====================================================
-- ALTER TABLE mentors 
-- ADD COLUMN designation VARCHAR(255) AFTER mentor_department,
-- ADD COLUMN profile_picture VARCHAR(500) AFTER designation;

-- =====================================================
-- Verify the changes
-- =====================================================
-- DESCRIBE mentors;
-- or
-- SHOW COLUMNS FROM mentors;









