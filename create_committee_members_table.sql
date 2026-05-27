-- Create committee_members table for three-tier dashboards (Leader, Working Committee, Department Faculty)
-- Run this in your MySQL client if you prefer manual migration: mysql -u user -p database < create_committee_members_table.sql

CREATE TABLE IF NOT EXISTS committee_members (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(255) NULL,
    allocated_departments TEXT NULL
);
