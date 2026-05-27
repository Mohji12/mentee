-- Run this on existing databases that already have the meetings table.
-- New installs use create_all_tables.sql which includes these columns.
-- Skip if you get "Duplicate column" errors (columns already exist).

ALTER TABLE meetings ADD COLUMN meeting_mode VARCHAR(20) DEFAULT 'offline';
ALTER TABLE meetings ADD COLUMN google_meet_link VARCHAR(500) NULL;
