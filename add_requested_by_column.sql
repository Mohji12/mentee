-- Add requested_by column to distinguish mentee-requested vs mentor-requested activities.
-- Run once: ALTER TABLE activities_tracking ADD COLUMN requested_by VARCHAR(20) NULL;

ALTER TABLE activities_tracking
ADD COLUMN requested_by VARCHAR(20) NULL;
