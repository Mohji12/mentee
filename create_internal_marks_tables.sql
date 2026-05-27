-- Consolidated internal marks (mentor view + admin import)
-- Run once against MySQL.

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS internal_marks_import_batch (
    id INT PRIMARY KEY AUTO_INCREMENT,
    semester INT NOT NULL,
    section_code VARCHAR(64) NULL,
    program_label VARCHAR(512) NULL,
    branch_label VARCHAR(512) NULL,
    title VARCHAR(1024) NULL,
    academic_year VARCHAR(32) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NULL,
    INDEX idx_internal_marks_batch_semester (semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS internal_marks_entry (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT NOT NULL,
    student_usn VARCHAR(255) NOT NULL,
    semester INT NOT NULL,
    subject_code VARCHAR(64) NOT NULL,
    subject_name VARCHAR(512) NULL,
    component_key VARCHAR(128) NOT NULL,
    component_label VARCHAR(255) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    score VARCHAR(32) NULL,
    CONSTRAINT fk_internal_marks_entry_batch
        FOREIGN KEY (batch_id) REFERENCES internal_marks_import_batch(id) ON DELETE CASCADE,
    CONSTRAINT fk_internal_marks_entry_student
        FOREIGN KEY (student_usn) REFERENCES students(student_usn) ON DELETE CASCADE,
    UNIQUE KEY uq_internal_marks_entry_batch_usn_subj_comp (batch_id, student_usn, subject_code, component_key),
    INDEX idx_internal_marks_entry_student_sem (student_usn, semester),
    INDEX idx_internal_marks_entry_batch_sem (batch_id, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
