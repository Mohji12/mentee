-- Create counseling_reminders table for notification system
CREATE TABLE IF NOT EXISTS counseling_reminders (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES counseling_sessions(counseling_id),
    recipient_id VARCHAR(255) NOT NULL,
    recipient_type VARCHAR(20) NOT NULL,
    reminder_type VARCHAR(30) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    scheduled_for TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    read_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_reminder_recipient ON counseling_reminders(recipient_id, recipient_type);
CREATE INDEX IF NOT EXISTS idx_reminder_status ON counseling_reminders(status);
CREATE INDEX IF NOT EXISTS idx_reminder_scheduled ON counseling_reminders(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_reminder_session ON counseling_reminders(session_id);
