-- ====================================================
-- Sample Data Insertion Script (seed.sql)
-- System: Employee Attendance, Shift & Leave Management System
-- Database Name: attendance_db
-- ====================================================

USE attendance_db;

-- 1. Departments
INSERT INTO department (dept_id, dept_name, location) VALUES
(1, 'HR', 'Building A, Floor 2'),
(2, 'IT', 'Building B, Floor 4'),
(3, 'Finance', 'Building A, Floor 3'),
(4, 'Sales', 'Building C, Floor 1'),
(5, 'Operations', 'Building B, Floor 1');

-- 2. Employees
INSERT INTO employee (emp_id, name, email, phone, hire_date, dept_id) VALUES
(1, 'Asha Reddy', 'asha.reddy@example.com', '9876543210', '2023-01-15', 1),
(2, 'Ravi Kumar', 'ravi.kumar@example.com', '9876543211', '2022-05-20', 2),
(3, 'Sneha Rao', 'sneha.rao@example.com', '9876543212', '2023-08-10', 2),
(4, 'Imran Khan', 'imran.khan@example.com', '9876543213', '2021-11-01', 3),
(5, 'Lakshmi Devi', 'lakshmi.devi@example.com', '9876543214', '2024-02-01', 4);

-- 3. Shifts
INSERT INTO shift (shift_id, shift_name, start_time, end_time) VALUES
(1, 'Morning Shift', '09:00:00', '17:00:00'),
(2, 'Evening Shift', '14:00:00', '22:00:00'),
(3, 'Night Shift', '22:00:00', '06:00:00');

-- 4. Shift Assignments
INSERT INTO shift_assignment (assign_id, emp_id, shift_id, work_date) VALUES
(1, 1, 1, '2026-10-05'),
(2, 2, 1, '2026-10-05'),
(3, 3, 2, '2026-10-05'),
(4, 4, 1, '2026-10-05'),
(5, 5, 2, '2026-10-05');

-- 5. Attendance Records
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

-- 6. Leave Types
INSERT INTO leave_type (type_id, type_name, max_days) VALUES
(1, 'Casual Leave', 12),
(2, 'Sick Leave', 10),
(3, 'Annual Leave', 20),
(4, 'Emergency Leave', 5);

-- 7. Leave Requests
INSERT INTO leave_request (leave_id, emp_id, type_id, start_date, end_date, reason, status) VALUES
(1, 5, 1, '2026-10-05', '2026-10-07', 'Family function', 'Approved'),
(2, 2, 2, '2026-10-10', '2026-10-12', 'Medical recovery', 'Approved'),
(3, 1, 3, '2026-10-15', '2026-10-20', 'Vacation leave', 'Pending'),
(4, 4, 1, '2026-10-05', '2026-10-05', 'Personal urgent work', 'Approved'),
(5, 3, 4, '2026-10-02', '2026-10-03', 'Emergency work', 'Rejected');

-- 8. Admin Users
INSERT INTO admin_user (admin_id, username, password_hash, full_name, email, role, is_active) VALUES
(1, 'admin', 'admin123', 'System Administrator', 'admin@attendx.com', 'Super Admin', 1),
(2, 'priya_hr', 'hrpass123', 'Priya Sharma', 'priya.hr@attendx.com', 'HR Admin', 1),
(3, 'karthik_ops', 'opspass123', 'Karthik Verma', 'karthik.ops@attendx.com', 'Operations Admin', 1);

-- 9. Admin Audit Logs
INSERT INTO admin_audit_log (log_id, admin_id, action_type, target_table, target_id, description) VALUES
(1, 1, 'SYSTEM_INIT', 'database', NULL, 'Database schema initialized with 3NF structure and seed data'),
(2, 2, 'APPROVE_LEAVE', 'leave_request', 1, 'Approved Casual Leave for Lakshmi Devi (2026-10-05 to 2026-10-07)'),
(3, 3, 'ASSIGN_SHIFT', 'shift_assignment', 1, 'Assigned Morning Shift to Asha Reddy for 2026-10-05'),
(4, 2, 'APPROVE_LEAVE', 'leave_request', 4, 'Approved Casual Leave for Imran Khan'),
(5, 1, 'POLICY_UPDATE', 'leave_type', 3, 'Updated Annual Leave allowance policy');
