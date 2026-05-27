-- Add submitted_at column to existing mentoring_assessments table
ALTER TABLE mentoring_assessments 
ADD COLUMN submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Update existing records with current timestamp (optional)
UPDATE mentoring_assessments 
SET submitted_at = CURRENT_TIMESTAMP 
WHERE submitted_at IS NULL;

-- Verify the column was added
DESCRIBE mentoring_assessments; 