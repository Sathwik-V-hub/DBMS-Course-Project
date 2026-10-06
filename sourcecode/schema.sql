-- ====================================================
-- Employee Attendance, Shift & Leave Management System
-- Database Schema Definition (attendance_db)
-- Storage Engine: InnoDB | Encoding: UTF-8 (utf8mb4)
-- ====================================================

CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- Drop views in reverse order
DROP VIEW IF EXISTS leave_summary;
DROP VIEW IF EXISTS attendance_summary;
DROP VIEW IF EXISTS current_shift_roster;
DROP VIEW IF EXISTS employee_department_view;

-- Drop tables in reverse foreign key order
DROP TABLE IF EXISTS leave_request;
DROP TABLE IF EXISTS leave_type;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS shift_assignment;
DROP TABLE IF EXISTS shift;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS department;

-- 1. DEPARTMENT TABLE
CREATE TABLE department (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. EMPLOYEE TABLE
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. SHIFT TABLE
CREATE TABLE shift (
    shift_id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(30) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. SHIFT_ASSIGNMENT TABLE (M:N Employee ↔ Shift)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. ATTENDANCE TABLE
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. LEAVE_TYPE TABLE
CREATE TABLE leave_type (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(30) NOT NULL UNIQUE,
    max_days INT NOT NULL CHECK(max_days > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. LEAVE_REQUEST TABLE
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- INDEXES
CREATE INDEX idx_employee_dept ON employee(dept_id);
CREATE INDEX idx_leave_request_emp ON leave_request(emp_id);
CREATE INDEX idx_leave_request_status ON leave_request(status);
CREATE INDEX idx_leave_request_dates ON leave_request(start_date, end_date);

-- DATABASE VIEWS
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
