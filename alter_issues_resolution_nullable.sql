-- Make resolution columns nullable so mentee can submit issues first; mentor fills resolution later.
-- Run this if session_issues_resolutions already exists with NOT NULL resolution columns.

-- MySQL
ALTER TABLE session_issues_resolutions MODIFY COLUMN resolution_details TEXT NULL;
ALTER TABLE session_issues_resolutions MODIFY COLUMN date_resolution_provided DATE NULL;
