-- Student dashboard enhancement: employability, alumni/expert sessions, notifications

CREATE TABLE IF NOT EXISTS employability_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_usn VARCHAR(255) NOT NULL,
    score INT NOT NULL,
    performance_level VARCHAR(50) NOT NULL,
    assessed_by VARCHAR(255) NULL,
    assessed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT NULL,
    INDEX idx_employability_student (student_usn),
    CONSTRAINT fk_employability_student FOREIGN KEY (student_usn) REFERENCES students (student_usn) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alumni_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_title VARCHAR(255) NOT NULL,
    session_date DATETIME NOT NULL,
    speaker_name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_by VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alumni_session_date (session_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alumni_session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'attended',
    marked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alumni_att_session (session_id),
    INDEX idx_alumni_att_usn (student_usn),
    CONSTRAINT fk_alumni_att_session FOREIGN KEY (session_id) REFERENCES alumni_sessions (id) ON DELETE CASCADE,
    CONSTRAINT fk_alumni_att_student FOREIGN KEY (student_usn) REFERENCES students (student_usn) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expert_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_title VARCHAR(255) NOT NULL,
    session_date DATETIME NOT NULL,
    expert_name VARCHAR(255) NOT NULL,
    expert_type VARCHAR(50) NOT NULL DEFAULT 'industry',
    description TEXT NULL,
    created_by VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expert_session_date (session_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expert_session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'attended',
    marked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expert_att_session (session_id),
    INDEX idx_expert_att_usn (student_usn),
    CONSTRAINT fk_expert_att_session FOREIGN KEY (session_id) REFERENCES expert_sessions (id) ON DELETE CASCADE,
    CONSTRAINT fk_expert_att_student FOREIGN KEY (student_usn) REFERENCES students (student_usn) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_usn VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'announcement',
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    link VARCHAR(500) NULL,
    INDEX idx_notifications_student (student_usn),
    INDEX idx_notifications_created (created_at),
    CONSTRAINT fk_notifications_student FOREIGN KEY (student_usn) REFERENCES students (student_usn) ON DELETE CASCADE
) ENGINE=InnoDB;
