-- Create counseling_escalations table for admin/HOD oversight
CREATE TABLE IF NOT EXISTS counseling_escalations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES counseling_sessions(counseling_id),
    escalated_by VARCHAR(255) NOT NULL,
    escalated_to VARCHAR(255) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_escalation_session_id ON counseling_escalations(session_id);
CREATE INDEX IF NOT EXISTS idx_escalation_status ON counseling_escalations(status);
CREATE INDEX IF NOT EXISTS idx_escalation_escalated_to ON counseling_escalations(escalated_to);
CREATE INDEX IF NOT EXISTS idx_escalation_priority ON counseling_escalations(priority);
