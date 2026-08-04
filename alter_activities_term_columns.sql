-- AI-generated activity descriptions can exceed VARCHAR(255)
ALTER TABLE activities
    MODIFY COLUMN short_term TEXT NULL,
    MODIFY COLUMN short_term1 TEXT NULL,
    MODIFY COLUMN short_term2 TEXT NULL,
    MODIFY COLUMN mid_term TEXT NULL,
    MODIFY COLUMN mid_term1 TEXT NULL,
    MODIFY COLUMN mid_term2 TEXT NULL,
    MODIFY COLUMN long_term TEXT NULL,
    MODIFY COLUMN long_term1 TEXT NULL,
    MODIFY COLUMN long_term2 TEXT NULL;
