-- ====================================================
-- UNIFIED DATABASE SCRIPT (database.sql)
-- System: Employee Attendance, Shift & Leave Management System
-- Database Name: attendance_db
-- Storage Engine: InnoDB | Encoding: UTF-8 (utf8mb4)
-- Purpose: Single-file import for MySQL Workbench & MySQL CLI
-- ====================================================

-- ----------------------------------------------------
-- 1. DATABASE CREATION & CONTEXT
-- ----------------------------------------------------
CREATE DATABASE IF NOT EXISTS attendance_db
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE attendance_db;

-- ----------------------------------------------------
-- 2. CLEANUP EXISTING VIEWS & TABLES
-- ----------------------------------------------------
DROP VIEW IF EXISTS system_admin_overview;
DROP VIEW IF EXISTS admin_activity_log_view;
DROP VIEW IF EXISTS leave_summary;
DROP VIEW IF EXISTS attendance_summary;
DROP VIEW IF EXISTS current_shift_roster;
DROP VIEW IF EXISTS employee_department_view;

DROP TABLE IF EXISTS admin_audit_log;
DROP TABLE IF EXISTS admin_user;
DROP TABLE IF EXISTS leave_request;
DROP TABLE IF EXISTS leave_type;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS shift_assignment;
DROP TABLE IF EXISTS shift;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS department;

-- ----------------------------------------------------
-- 3. CREATE TABLES & CONSTRAINTS
-- ----------------------------------------------------

-- Table 1: department
CREATE TABLE department (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: employee (Note: Name is singular 'employee', NOT 'employees')
CREATE TABLE employee (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    email VARCHAR(80) NOT NULL UNIQUE,
    phone VARCHAR(15),
    hire_date DATE NOT NULL,
    dept_id INT NOT NULL,
    FOREIGN KEY (dept_id)
        REFERENCES department(dept_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 3: shift
CREATE TABLE shift (
    shift_id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(30) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 4: shift_assignment (M:N Employee ↔ Shift)
CREATE TABLE shift_assignment (
    assign_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    shift_id INT NOT NULL,
    work_date DATE NOT NULL,
    UNIQUE(emp_id, work_date),
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (shift_id)
        REFERENCES shift(shift_id)
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 5: attendance
CREATE TABLE attendance (
    att_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    att_date DATE NOT NULL,
    check_in TIME,
    check_out TIME,
    status ENUM('Present', 'Absent', 'Late', 'On Leave') NOT NULL DEFAULT 'Present',
    UNIQUE(emp_id, att_date),
    CHECK (check_in IS NULL OR check_out IS NULL OR check_out > check_in),
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 6: leave_type
CREATE TABLE leave_type (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(30) NOT NULL UNIQUE,
    max_days INT NOT NULL CHECK(max_days > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 7: leave_request
CREATE TABLE leave_request (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT NOT NULL,
    type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason VARCHAR(200),
    status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
    CHECK (end_date >= start_date),
    FOREIGN KEY (emp_id)
        REFERENCES employee(emp_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (type_id)
        REFERENCES leave_type(type_id)
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 8: admin_user (System Administrator Accounts & Roles)
CREATE TABLE admin_user (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(80) NOT NULL,
    email VARCHAR(80) NOT NULL UNIQUE,
    role ENUM('Super Admin', 'HR Admin', 'Operations Admin') NOT NULL DEFAULT 'HR Admin',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 9: admin_audit_log (Tracks Administrator Actions & Modifications)
CREATE TABLE admin_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_table VARCHAR(50) NOT NULL,
    target_id INT,
    description TEXT,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id)
        REFERENCES admin_user(admin_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------
-- 4. CREATE INDEXES
-- ----------------------------------------------------
CREATE INDEX idx_employee_dept ON employee(dept_id);
CREATE INDEX idx_leave_request_emp ON leave_request(emp_id);
CREATE INDEX idx_leave_request_status ON leave_request(status);
CREATE INDEX idx_leave_request_dates ON leave_request(start_date, end_date);
CREATE INDEX idx_admin_user_role ON admin_user(role);
CREATE INDEX idx_audit_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_action ON admin_audit_log(action_type);

-- ----------------------------------------------------
-- 5. CREATE VIEWS
-- ----------------------------------------------------
CREATE VIEW employee_department_view AS
SELECT 
    e.emp_id,
    e.name AS employee_name,
    e.email,
    e.phone,
    d.dept_name AS department,
    d.location
FROM employee e
JOIN department d ON e.dept_id = d.dept_id;

CREATE VIEW current_shift_roster AS
SELECT 
    sa.assign_id,
    sa.emp_id,
    sa.shift_id,
    e.name AS employee,
    d.dept_name AS department,
    s.shift_name AS shift,
    s.start_time,
    s.end_time,
    sa.work_date
FROM shift_assignment sa
JOIN employee e ON sa.emp_id = e.emp_id
JOIN department d ON e.dept_id = d.dept_id
JOIN shift s ON sa.shift_id = s.shift_id;

CREATE VIEW attendance_summary AS
SELECT 
    e.name AS employee,
    a.status AS attendance_status,
    a.att_date AS attendance_date
FROM attendance a
JOIN employee e ON a.emp_id = e.emp_id;

CREATE VIEW leave_summary AS
SELECT 
    e.name AS employee,
    lt.type_name AS leave_type,
    lr.start_date,
    lr.end_date,
    lr.reason,
    lr.status
FROM leave_request lr
JOIN employee e ON lr.emp_id = e.emp_id
JOIN leave_type lt ON lr.type_id = lt.type_id;

CREATE VIEW admin_activity_log_view AS
SELECT 
    al.log_id,
    au.username AS admin_user,
    au.full_name AS admin_name,
    au.role AS admin_role,
    al.action_type,
    al.target_table,
    al.target_id,
    al.description,
    al.action_timestamp
FROM admin_audit_log al
JOIN admin_user au ON al.admin_id = au.admin_id;

CREATE VIEW system_admin_overview AS
SELECT 
    (SELECT COUNT(*) FROM employee) AS total_employees,
    (SELECT COUNT(*) FROM department) AS total_departments,
    (SELECT COUNT(*) FROM shift) AS total_shifts,
    (SELECT COUNT(*) FROM leave_request WHERE status = 'Pending') AS pending_leaves,
    (SELECT COUNT(*) FROM attendance WHERE status = 'Present') AS total_present_records,
    (SELECT COUNT(*) FROM admin_user WHERE is_active = 1) AS active_admins;

-- ----------------------------------------------------
-- 6. SAMPLE DATA INSERTION (SEED)
-- ----------------------------------------------------
INSERT INTO department (dept_id, dept_name, location) VALUES
(1, 'HR', 'Building A, Floor 2'),
(2, 'IT', 'Building B, Floor 4'),
(3, 'Finance', 'Building A, Floor 3'),
(4, 'Sales', 'Building C, Floor 1'),
(5, 'Operations', 'Building B, Floor 1');

INSERT INTO employee (emp_id, name, email, phone, hire_date, dept_id) VALUES
(1, 'Asha Reddy', 'asha.reddy@example.com', '9876543210', '2023-01-15', 1),
(2, 'Ravi Kumar', 'ravi.kumar@example.com', '9876543211', '2022-05-20', 2),
(3, 'Sneha Rao', 'sneha.rao@example.com', '9876543212', '2023-08-10', 2),
(4, 'Imran Khan', 'imran.khan@example.com', '9876543213', '2021-11-01', 3),
(5, 'Lakshmi Devi', 'lakshmi.devi@example.com', '9876543214', '2024-02-01', 4);

INSERT INTO shift (shift_id, shift_name, start_time, end_time) VALUES
(1, 'Morning Shift', '09:00:00', '17:00:00'),
(2, 'Evening Shift', '14:00:00', '22:00:00'),
(3, 'Night Shift', '22:00:00', '06:00:00');

INSERT INTO shift_assignment (assign_id, emp_id, shift_id, work_date) VALUES
(1, 1, 1, '2026-10-05'),
(2, 2, 1, '2026-10-05'),
(3, 3, 2, '2026-10-05'),
(4, 4, 1, '2026-10-05'),
(5, 5, 2, '2026-10-05');

INSERT INTO attendance (att_id, emp_id, att_date, check_in, check_out, status) VALUES
(1, 1, '2026-10-06', '08:50:00', '17:05:00', 'Present'),
(2, 2, '2026-10-06', '09:42:00', '17:15:00', 'Late'),
(3, 3, '2026-10-06', '08:58:00', '17:00:00', 'Present'),
(4, 4, '2026-10-06', NULL, NULL, 'Absent'),
(5, 5, '2026-10-06', NULL, NULL, 'On Leave'),
(6, 1, '2026-10-05', '08:55:00', '17:05:00', 'Present'),
(7, 2, '2026-10-05', '09:20:00', '17:00:00', 'Late'),
(8, 3, '2026-10-05', '14:00:00', '22:00:00', 'Present'),
(9, 4, '2026-10-05', NULL, NULL, 'Absent'),
(10, 5, '2026-10-05', NULL, NULL, 'On Leave');

INSERT INTO leave_type (type_id, type_name, max_days) VALUES
(1, 'Casual Leave', 12),
(2, 'Sick Leave', 10),
(3, 'Annual Leave', 20),
(4, 'Emergency Leave', 5);

INSERT INTO leave_request (leave_id, emp_id, type_id, start_date, end_date, reason, status) VALUES
(1, 5, 1, '2026-10-05', '2026-10-07', 'Family function', 'Approved'),
(2, 2, 2, '2026-10-10', '2026-10-12', 'Medical recovery', 'Approved'),
(3, 1, 3, '2026-10-15', '2026-10-20', 'Vacation leave', 'Pending'),
(4, 4, 1, '2026-10-05', '2026-10-05', 'Personal urgent work', 'Approved'),
(5, 3, 4, '2026-10-02', '2026-10-03', 'Emergency work', 'Rejected');

INSERT INTO admin_user (admin_id, username, password_hash, full_name, email, role, is_active) VALUES
(1, 'admin', 'admin123', 'System Administrator', 'admin@attendx.com', 'Super Admin', 1),
(2, 'priya_hr', 'hrpass123', 'Priya Sharma', 'priya.hr@attendx.com', 'HR Admin', 1),
(3, 'karthik_ops', 'opspass123', 'Karthik Verma', 'karthik.ops@attendx.com', 'Operations Admin', 1);

INSERT INTO admin_audit_log (log_id, admin_id, action_type, target_table, target_id, description) VALUES
(1, 1, 'SYSTEM_INIT', 'database', NULL, 'Database schema initialized with 3NF structure and seed data'),
(2, 2, 'APPROVE_LEAVE', 'leave_request', 1, 'Approved Casual Leave for Lakshmi Devi (2026-10-05 to 2026-10-07)'),
(3, 3, 'ASSIGN_SHIFT', 'shift_assignment', 1, 'Assigned Morning Shift to Asha Reddy for 2026-10-05'),
(4, 2, 'APPROVE_LEAVE', 'leave_request', 4, 'Approved Casual Leave for Imran Khan'),
(5, 1, 'POLICY_UPDATE', 'leave_type', 3, 'Updated Annual Leave allowance policy');

-- ----------------------------------------------------
-- 7. EASY SELECT QUERIES FOR ALL TABLES
-- (Use singular table names below!)
-- ----------------------------------------------------

SELECT * FROM department;
SELECT * FROM employee;          -- Correct name: employee (NOT employees)
SELECT * FROM shift;
SELECT * FROM shift_assignment;
SELECT * FROM attendance;
SELECT * FROM leave_type;
SELECT * FROM leave_request;
SELECT * FROM admin_user;
SELECT * FROM admin_audit_log;

-- ----------------------------------------------------
-- 8. REQUIRED CORE QUERIES (SECTION 14)
-- ----------------------------------------------------

-- QUERY 1: Display today's shift roster
SELECT 
    e.name AS employee_name,
    d.dept_name AS department,
    s.shift_name,
    s.start_time,
    s.end_time,
    sa.work_date
FROM shift_assignment sa
JOIN employee e ON e.emp_id = sa.emp_id
JOIN department d ON d.dept_id = e.dept_id
JOIN shift s ON s.shift_id = sa.shift_id
WHERE sa.work_date = '2026-10-05';

-- QUERY 2: Attendance count by status
SELECT 
    status,
    COUNT(*) AS total_days
FROM attendance
GROUP BY status;

-- QUERY 3: Approved leave days per employee
SELECT 
    e.emp_id,
    e.name AS employee_name,
    d.dept_name AS department,
    SUM(DATEDIFF(lr.end_date, lr.start_date) + 1) AS total_approved_leave_days
FROM leave_request lr
JOIN employee e ON lr.emp_id = e.emp_id
JOIN department d ON e.dept_id = d.dept_id
WHERE lr.status = 'Approved'
GROUP BY e.emp_id, e.name, d.dept_name;

-- QUERY 4: Departments with 2 or more employees
SELECT 
    d.dept_name,
    d.location,
    COUNT(e.emp_id) AS headcount
FROM department d
JOIN employee e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name, d.location
HAVING COUNT(e.emp_id) >= 2;

-- ----------------------------------------------------
-- 9. VIEW EXECUTIONS
-- ----------------------------------------------------
SELECT * FROM employee_department_view;

SELECT * FROM current_shift_roster;
SELECT * FROM attendance_summary;
SELECT * FROM leave_summary;
SELECT * FROM admin_activity_log_view;
SELECT * FROM system_admin_overview;
