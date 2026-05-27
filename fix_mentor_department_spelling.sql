-- Fix spelling and normalize department names in mentors table
-- Run this against your database (e.g. mysql client or any SQL runner).
-- Adjust or add UPDATE statements to match your data.

-- Spelling: Mathematial -> Mathematical
UPDATE mentors SET mentor_department = 'Data Analytics & Mathematical Science' WHERE mentor_department = 'Data Analytics & Mathematial Science';
UPDATE mentors SET mentor_department = 'Mathematical Science' WHERE mentor_department = 'Mathematial Science';

-- Normalize "and" -> "&" to avoid duplicates (Physics and Electronics vs Physics & Electronics)
UPDATE mentors SET mentor_department = 'Physics & Electronics' WHERE mentor_department = 'Physics and Electronics';

-- Add more as needed, e.g.:
-- UPDATE mentors SET mentor_department = 'Biochemistry & Chemistry' WHERE mentor_department = 'Biochemistry and Chemistry';
-- UPDATE mentors SET mentor_department = 'Biotechnology & Genetics' WHERE mentor_department = 'Biotechnology and Genetics';
