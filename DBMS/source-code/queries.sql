-- ====================================================
-- Required Queries & BI Reports (queries.sql)
-- System: Employee Attendance, Shift & Leave Management System
-- Database Name: attendance_db
-- ====================================================

USE attendance_db;

-- ----------------------------------------------------
-- QUERY 1: Today's Shift Roster
-- ----------------------------------------------------
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

-- ----------------------------------------------------
-- QUERY 2: Attendance Count by Status
-- ----------------------------------------------------
SELECT 
    status,
    COUNT(*) AS total_days
FROM attendance
GROUP BY status;

-- ----------------------------------------------------
-- QUERY 3: Approved Leave Days per Employee
-- ----------------------------------------------------
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

-- ----------------------------------------------------
-- QUERY 4: Departments with 2 or More Employees
-- ----------------------------------------------------
SELECT 
    d.dept_name,
    d.location,
    COUNT(e.emp_id) AS headcount
FROM department d
JOIN employee e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name, d.location
HAVING COUNT(e.emp_id) >= 2;

-- ----------------------------------------------------
-- DATABASE VIEW INSPECTIONS
-- ----------------------------------------------------
SELECT * FROM employee_department_view;
SELECT * FROM current_shift_roster;
SELECT * FROM attendance_summary;
SELECT * FROM leave_summary;
