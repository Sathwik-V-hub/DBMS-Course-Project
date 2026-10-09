import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "employee_attendance_secret_key"

# Database Configuration Defaults
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DB', 'attendance_db'),
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def get_db_connection():
    try:
        import mysql.connector
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn, "mysql"
    except Exception:
        sqlite_db_path = os.path.join(os.path.dirname(__file__), "attendance_fallback.db")
        conn = sqlite3.connect(sqlite_db_path)
        conn.row_factory = sqlite3.Row
        init_sqlite_fallback(conn)
        return conn, "sqlite"

def init_sqlite_fallback(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='department';")
    if not cursor.fetchone():
        cursor.executescript("""
    CREATE TABLE department (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL UNIQUE,
        location TEXT
    );

    CREATE TABLE employee (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        hire_date TEXT NOT NULL,
        dept_id INTEGER NOT NULL,
        FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE RESTRICT
    );

    CREATE TABLE shift (
        shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shift_name TEXT NOT NULL UNIQUE,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    );

    CREATE TABLE shift_assignment (
        assign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        work_date TEXT NOT NULL,
        UNIQUE(emp_id, work_date),
        FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE,
        FOREIGN KEY (shift_id) REFERENCES shift(shift_id)
    );

    CREATE TABLE attendance (
        att_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        att_date TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        status TEXT CHECK(status IN ('Present', 'Absent', 'Late', 'On Leave')) NOT NULL DEFAULT 'Present',
        UNIQUE(emp_id, att_date),
        CHECK (check_in IS NULL OR check_out IS NULL OR check_out > check_in),
        FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
    );

    CREATE TABLE leave_type (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT NOT NULL UNIQUE,
        max_days INTEGER NOT NULL CHECK(max_days > 0)
    );

    CREATE TABLE leave_request (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        type_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        reason TEXT,
        status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected')) NOT NULL DEFAULT 'Pending',
        CHECK(end_date >= start_date),
        FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE,
        FOREIGN KEY (type_id) REFERENCES leave_type(type_id)
    );

    CREATE TABLE IF NOT EXISTS admin_user (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL DEFAULT 'HR Admin',
        is_active INTEGER NOT NULL DEFAULT 1,
        last_login TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS admin_audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        target_table TEXT NOT NULL,
        target_id INTEGER,
        description TEXT,
        action_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES admin_user(admin_id) ON DELETE CASCADE
    );

    -- Views
    CREATE VIEW IF NOT EXISTS employee_department_view AS
    SELECT e.emp_id, e.name AS employee_name, e.email, e.phone, d.dept_name AS department, d.location
    FROM employee e JOIN department d ON e.dept_id = d.dept_id;

    CREATE VIEW IF NOT EXISTS current_shift_roster AS
    SELECT sa.assign_id, sa.emp_id, sa.shift_id, e.name AS employee, d.dept_name AS department, s.shift_name AS shift, s.start_time, s.end_time, sa.work_date
    FROM shift_assignment sa
    JOIN employee e ON sa.emp_id = e.emp_id
    JOIN department d ON e.dept_id = d.dept_id
    JOIN shift s ON sa.shift_id = s.shift_id;

    CREATE VIEW IF NOT EXISTS attendance_summary AS
    SELECT e.name AS employee, a.status AS attendance_status, a.att_date AS attendance_date
    FROM attendance a JOIN employee e ON a.emp_id = e.emp_id;

    CREATE VIEW IF NOT EXISTS leave_summary AS
    SELECT e.name AS employee, lt.type_name AS leave_type, lr.start_date, lr.end_date, lr.reason, lr.status
    FROM leave_request lr
    JOIN employee e ON lr.emp_id = e.emp_id
    JOIN leave_type lt ON lr.type_id = lt.type_id;

    CREATE VIEW IF NOT EXISTS admin_activity_log_view AS
    SELECT al.log_id, au.username AS admin_user, au.full_name AS admin_name, au.role AS admin_role,
           al.action_type, al.target_table, al.target_id, al.description, al.action_timestamp
    FROM admin_audit_log al
    JOIN admin_user au ON al.admin_id = au.admin_id;

    CREATE VIEW IF NOT EXISTS system_admin_overview AS
    SELECT (SELECT COUNT(*) FROM employee) AS total_employees,
           (SELECT COUNT(*) FROM department) AS total_departments,
           (SELECT COUNT(*) FROM shift) AS total_shifts,
           (SELECT COUNT(*) FROM leave_request WHERE status = 'Pending') AS pending_leaves,
           (SELECT COUNT(*) FROM attendance WHERE status = 'Present') AS total_present_records,
           (SELECT COUNT(*) FROM admin_user WHERE is_active = 1) AS active_admins;

    -- Seed Data
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
    """)
    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log';")
    if not cursor.fetchone():
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS admin_user (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'HR Admin',
            is_active INTEGER NOT NULL DEFAULT 1,
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admin_audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            target_table TEXT NOT NULL,
            target_id INTEGER,
            description TEXT,
            action_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES admin_user(admin_id) ON DELETE CASCADE
        );

        CREATE VIEW IF NOT EXISTS admin_activity_log_view AS
        SELECT al.log_id, au.username AS admin_user, au.full_name AS admin_name, au.role AS admin_role,
               al.action_type, al.target_table, al.target_id, al.description, al.action_timestamp
        FROM admin_audit_log al
        JOIN admin_user au ON al.admin_id = au.admin_id;

        CREATE VIEW IF NOT EXISTS system_admin_overview AS
        SELECT (SELECT COUNT(*) FROM employee) AS total_employees,
               (SELECT COUNT(*) FROM department) AS total_departments,
               (SELECT COUNT(*) FROM shift) AS total_shifts,
               (SELECT COUNT(*) FROM leave_request WHERE status = 'Pending') AS pending_leaves,
               (SELECT COUNT(*) FROM attendance WHERE status = 'Present') AS total_present_records,
               (SELECT COUNT(*) FROM admin_user WHERE is_active = 1) AS active_admins;

        INSERT OR IGNORE INTO admin_user (admin_id, username, password_hash, full_name, email, role, is_active) VALUES
        (1, 'admin', 'admin123', 'System Administrator', 'admin@attendx.com', 'Super Admin', 1),
        (2, 'priya_hr', 'hrpass123', 'Priya Sharma', 'priya.hr@attendx.com', 'HR Admin', 1),
        (3, 'karthik_ops', 'opspass123', 'Karthik Verma', 'karthik.ops@attendx.com', 'Operations Admin', 1);

        INSERT OR IGNORE INTO admin_audit_log (log_id, admin_id, action_type, target_table, target_id, description) VALUES
        (1, 1, 'SYSTEM_INIT', 'database', NULL, 'Database schema initialized with 3NF structure and seed data'),
        (2, 2, 'APPROVE_LEAVE', 'leave_request', 1, 'Approved Casual Leave for Lakshmi Devi (2026-10-05 to 2026-10-07)'),
        (3, 3, 'ASSIGN_SHIFT', 'shift_assignment', 1, 'Assigned Morning Shift to Asha Reddy for 2026-10-05'),
        (4, 2, 'APPROVE_LEAVE', 'leave_request', 4, 'Approved Casual Leave for Imran Khan'),
        (5, 1, 'POLICY_UPDATE', 'leave_type', 3, 'Updated Annual Leave allowance policy');
        """)
        conn.commit()

def run_query(query, params=(), fetch_all=True, is_write=False):
    conn, engine = get_db_connection()
    try:
        if engine == "mysql":
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute(query, params)
            if is_write:
                conn.commit()
                res = cursor.lastrowid
            else:
                res = cursor.fetchall() if fetch_all else cursor.fetchone()
            cursor.close()
            conn.close()
            return res, engine
        else:
            cursor = conn.cursor()
            sqlite_query = query.replace('%s', '?')
            cursor.execute(sqlite_query, params)
            if is_write:
                conn.commit()
                res = cursor.lastrowid
            else:
                rows = cursor.fetchall() if fetch_all else cursor.fetchone()
                if fetch_all:
                    res = [dict(row) for row in rows]
                else:
                    res = dict(rows) if rows else None
            conn.close()
            return res, engine
    except Exception as err:
        if conn:
            conn.close()
        raise err

def log_admin_action(admin_id=1, action_type="ADMIN_ACTION", target_table="", target_id=None, description=""):
    try:
        run_query("""
            INSERT INTO admin_audit_log (admin_id, action_type, target_table, target_id, description)
            VALUES (%s, %s, %s, %s, %s);
        """, (admin_id, action_type, target_table, target_id, description), is_write=True)
    except Exception:
        pass

# ----------------------------------------------------
# ROUTES & CONTROLLERS
# ----------------------------------------------------

@app.route('/')
def dashboard():
    today_str = date.today().isoformat()
    try:
        dept_count, engine = run_query("SELECT COUNT(*) AS total FROM department;", fetch_all=False)
        emp_count, _ = run_query("SELECT COUNT(*) AS total FROM employee;", fetch_all=False)
        shift_count, _ = run_query("SELECT COUNT(*) AS total FROM shift;", fetch_all=False)
        pending_leaves, _ = run_query("SELECT COUNT(*) AS total FROM leave_request WHERE status = 'Pending';", fetch_all=False)
        audit_count, _ = run_query("SELECT COUNT(*) AS total FROM admin_audit_log;", fetch_all=False)

        recent_attendance, _ = run_query("""
            SELECT e.name AS employee_name, d.dept_name, a.att_date, a.check_in, a.check_out, a.status
            FROM attendance a
            JOIN employee e ON a.emp_id = e.emp_id
            JOIN department d ON e.dept_id = d.dept_id
            ORDER BY a.att_date DESC, a.att_id DESC LIMIT 5;
        """)

        recent_leaves, _ = run_query("""
            SELECT lr.leave_id, e.name AS employee_name, lt.type_name, lr.start_date, lr.end_date, lr.status
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN leave_type lt ON lr.type_id = lt.type_id
            ORDER BY lr.leave_id DESC LIMIT 5;
        """)

        recent_audit, _ = run_query("""
            SELECT al.log_id, au.username, au.role, al.action_type, al.target_table, al.description, al.action_timestamp
            FROM admin_audit_log al
            JOIN admin_user au ON al.admin_id = au.admin_id
            ORDER BY al.log_id DESC LIMIT 5;
        """)

        employees_list, _ = run_query("""
            SELECT e.emp_id, e.name, d.dept_name 
            FROM employee e 
            JOIN department d ON e.dept_id = d.dept_id;
        """)

        metrics = {
            'departments': dept_count['total'] if dept_count else 0,
            'employees': emp_count['total'] if emp_count else 0,
            'shifts': shift_count['total'] if shift_count else 0,
            'pending_leaves': pending_leaves['total'] if pending_leaves else 0,
            'audit_count': audit_count['total'] if audit_count else 0,
            'engine': engine,
            'today': today_str
        }

        return render_template('dashboard.html', metrics=metrics, recent_attendance=recent_attendance, recent_leaves=recent_leaves, recent_audit=recent_audit, employees=employees_list)
    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")
        return render_template('dashboard.html', metrics={'today': today_str}, recent_attendance=[], recent_leaves=[], recent_audit=[], employees=[])

@app.route('/departments', methods=['GET', 'POST'])
def departments():
    if request.method == 'POST':
        action = request.form.get('action')
        dept_name = request.form.get('dept_name', '').strip()
        location = request.form.get('location', '').strip()

        if action == 'add':
            try:
                run_query("INSERT INTO department (dept_name, location) VALUES (%s, %s);", (dept_name, location), is_write=True)
                flash(f"Department '{dept_name}' added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add department: {str(e)}", "danger")

        elif action == 'delete':
            dept_id = request.form.get('dept_id')
            try:
                run_query("DELETE FROM department WHERE dept_id = %s;", (dept_id,), is_write=True)
                flash("Department deleted successfully!", "success")
            except Exception as e:
                flash(f"Cannot delete department (ON DELETE RESTRICT active): {str(e)}", "danger")

        return redirect(url_for('departments'))

    depts, _ = run_query("""
        SELECT d.dept_id, d.dept_name, d.location, COUNT(e.emp_id) AS headcount
        FROM department d
        LEFT JOIN employee e ON d.dept_id = e.dept_id
        GROUP BY d.dept_id, d.dept_name, d.location;
    """)
    return render_template('departments.html', departments=depts)

@app.route('/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            hire_date = request.form.get('hire_date')
            dept_id = request.form.get('dept_id')
            try:
                emp_id, _ = run_query("INSERT INTO employee (name, email, phone, hire_date, dept_id) VALUES (%s, %s, %s, %s, %s);",
                          (name, email, phone, hire_date, dept_id), is_write=True)
                
                # AI Auto-Assign Shift to New Employee
                shifts, _ = run_query("SELECT shift_id FROM shift;")
                if shifts:
                    assigned_shift_id = shifts[0]['shift_id'] if isinstance(shifts[0], dict) else shifts[0][0]
                    today_str = date.today().isoformat()
                    try:
                        run_query("INSERT INTO shift_assignment (emp_id, shift_id, work_date) VALUES (%s, %s, %s);",
                                  (emp_id, assigned_shift_id, today_str), is_write=True)
                    except Exception:
                        pass

                flash(f"Employee '{name}' registered successfully & AI auto-assigned shift!", "success")
            except Exception as e:
                flash(f"Failed to create employee: {str(e)}", "danger")

        elif action == 'delete':
            emp_id = request.form.get('emp_id')
            try:
                run_query("DELETE FROM employee WHERE emp_id = %s;", (emp_id,), is_write=True)
                flash("Employee deleted successfully!", "success")
            except Exception as e:
                flash(f"Failed to delete employee: {str(e)}", "danger")

        return redirect(url_for('employees'))

    emp_list, _ = run_query("SELECT * FROM employee_department_view;")
    dept_list, _ = run_query("SELECT dept_id, dept_name FROM department;")
    return render_template('employees.html', employees=emp_list, departments=dept_list)

@app.route('/shifts', methods=['GET', 'POST'])
def shifts():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_shift':
            shift_name = request.form.get('shift_name', '').strip()
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            try:
                run_query("INSERT INTO shift (shift_name, start_time, end_time) VALUES (%s, %s, %s);",
                          (shift_name, start_time, end_time), is_write=True)
                flash(f"Shift '{shift_name}' created successfully!", "success")
            except Exception as e:
                flash(f"Failed to create shift: {str(e)}", "danger")

        elif action == 'assign_shift':
            emp_id = request.form.get('emp_id')
            shift_id = request.form.get('shift_id')
            work_date = request.form.get('work_date')
            try:
                run_query("INSERT INTO shift_assignment (emp_id, shift_id, work_date) VALUES (%s, %s, %s);",
                          (emp_id, shift_id, work_date), is_write=True)
                flash("Shift assigned successfully!", "success")
            except Exception as e:
                flash(f"Assignment failed: {str(e)}", "danger")

        elif action == 'change_shift':
            assign_id = request.form.get('assign_id')
            new_shift_id = request.form.get('shift_id')
            try:
                run_query("UPDATE shift_assignment SET shift_id = %s WHERE assign_id = %s;", (new_shift_id, assign_id), is_write=True)
                flash("Shift updated successfully by User!", "success")
            except Exception as e:
                flash(f"Failed to update shift: {str(e)}", "danger")

        return redirect(url_for('shifts'))

    shift_list, _ = run_query("SELECT * FROM shift;")
    roster_list, _ = run_query("""
        SELECT sa.assign_id, sa.emp_id, sa.shift_id, e.name AS employee, d.dept_name AS department, s.shift_name AS shift, s.start_time, s.end_time, sa.work_date
        FROM shift_assignment sa
        JOIN employee e ON sa.emp_id = e.emp_id
        JOIN department d ON e.dept_id = d.dept_id
        JOIN shift s ON sa.shift_id = s.shift_id
        ORDER BY sa.work_date DESC, sa.assign_id DESC;
    """)
    emp_list, _ = run_query("SELECT emp_id, name FROM employee;")
    today_str = date.today().isoformat()
    return render_template('shifts.html', shifts=shift_list, roster=roster_list, employees=emp_list, today=today_str)

@app.route('/auto_assign_shifts', methods=['POST'])
def auto_assign_shifts():
    target_date = request.form.get('target_date') or date.today().isoformat()
    try:
        employees, _ = run_query("SELECT emp_id FROM employee;")
        shifts, _ = run_query("SELECT shift_id FROM shift ORDER BY shift_id ASC;")

        if not employees or not shifts:
            flash("No employees or shift definitions found to auto-assign!", "warning")
            return redirect(url_for('shifts'))

        shift_ids = [s['shift_id'] if isinstance(s, dict) else s[0] for s in shifts]
        assigned_count = 0

        for idx, emp in enumerate(employees):
            emp_id = emp['emp_id'] if isinstance(emp, dict) else emp[0]
            smart_shift_id = shift_ids[idx % len(shift_ids)]
            try:
                run_query("""
                    INSERT INTO shift_assignment (emp_id, shift_id, work_date)
                    VALUES (%s, %s, %s);
                """, (emp_id, smart_shift_id, target_date), is_write=True)
                assigned_count += 1
            except Exception:
                pass

        flash(f"🤖 AI Auto-Assign Engine assigned shifts for {assigned_count} employees on {target_date}!", "success")
    except Exception as e:
        flash(f"AI Auto-Assignment failed: {str(e)}", "danger")

    return redirect(url_for('shifts'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    today_str = date.today().isoformat()
    if request.method == 'POST':
        emp_id = request.form.get('emp_id')
        att_date = request.form.get('att_date') or today_str
        status = request.form.get('status', 'Present')

        check_in = request.form.get('check_in') or None
        check_out = request.form.get('check_out') or None

        if status == 'Present' and not check_in:
            check_in = '09:00:00'
            check_out = '17:00:00'
        elif status == 'Late' and not check_in:
            check_in = '09:30:00'
            check_out = '17:00:00'

        try:
            # Determine the engine to pick the right upsert syntax
            _, engine = get_db_connection()
            if engine == 'mysql':
                run_query("""
                    INSERT INTO attendance (emp_id, att_date, check_in, check_out, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE check_in=VALUES(check_in), check_out=VALUES(check_out), status=VALUES(status);
                """, (emp_id, att_date, check_in, check_out, status), is_write=True)
            else:
                run_query("""
                    INSERT OR REPLACE INTO attendance (emp_id, att_date, check_in, check_out, status)
                    VALUES (?, ?, ?, ?, ?);
                """, (emp_id, att_date, check_in, check_out, status), is_write=True)
            flash(f"Attendance recorded for {att_date} as '{status}'!", "success")
        except Exception as e:
            flash(f"Recording failed: {str(e)}", "danger")

        return redirect(url_for('attendance'))

    att_list, _ = run_query("""
        SELECT a.att_id, e.name AS employee_name, d.dept_name, a.att_date, a.check_in, a.check_out, a.status
        FROM attendance a
        JOIN employee e ON a.emp_id = e.emp_id
        JOIN department d ON e.dept_id = d.dept_id
        ORDER BY a.att_date DESC, a.att_id DESC;
    """)
    emp_list, _ = run_query("""
        SELECT e.emp_id, e.name, d.dept_name 
        FROM employee e 
        JOIN department d ON e.dept_id = d.dept_id;
    """)
    stats = {
        'total': len(att_list),
        'present': sum(1 for a in att_list if a.get('status') == 'Present'),
        'late': sum(1 for a in att_list if a.get('status') == 'Late'),
        'absent': sum(1 for a in att_list if a.get('status') == 'Absent'),
        'on_leave': sum(1 for a in att_list if a.get('status') == 'On Leave')
    }
    return render_template('attendance.html', attendance_logs=att_list, employees=emp_list, today=today_str, stats=stats)

@app.route('/leaves', methods=['GET', 'POST'])
def leaves():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'apply':
            emp_id = request.form.get('emp_id')
            type_id = request.form.get('type_id')
            leave_type_input = (request.form.get('leave_type') or '').strip()
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            reason = request.form.get('reason', '').strip()

            try:
                if not type_id and leave_type_input:
                    # Look for existing leave type with this name (case-insensitive)
                    existing, _ = run_query(
                        "SELECT type_id FROM leave_type WHERE LOWER(type_name) = LOWER(%s);",
                        (leave_type_input,)
                    )
                    if existing:
                        type_id = existing[0]['type_id']
                    else:
                        # Auto-create the leave type with 15 max days
                        run_query(
                            "INSERT INTO leave_type (type_name, max_days) VALUES (%s, %s);",
                            (leave_type_input, 15),
                            is_write=True
                        )
                        new_type, _ = run_query(
                            "SELECT type_id FROM leave_type WHERE LOWER(type_name) = LOWER(%s);",
                            (leave_type_input,)
                        )
                        if new_type:
                            type_id = new_type[0]['type_id']

                if not type_id:
                    raise Exception("Please specify a valid leave category.")

                run_query("""
                    INSERT INTO leave_request (emp_id, type_id, start_date, end_date, reason, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pending');
                """, (emp_id, type_id, start_date, end_date, reason), is_write=True)
                flash("Leave request submitted successfully!", "success")
            except Exception as e:
                flash(f"Leave application failed: {str(e)}", "danger")

        elif action in ['Approved', 'Rejected']:
            leave_id = request.form.get('leave_id')
            try:
                run_query("UPDATE leave_request SET status = %s WHERE leave_id = %s;", (action, leave_id), is_write=True)
                flash(f"Leave request updated to '{action}'", "info")
            except Exception as e:
                flash(f"Failed to update leave status: {str(e)}", "danger")

        elif action == 'add_type':
            type_name = request.form.get('type_name', '').strip()
            max_days = request.form.get('max_days', '10')
            try:
                run_query("INSERT INTO leave_type (type_name, max_days) VALUES (%s, %s);",
                          (type_name, int(max_days)), is_write=True)
                flash(f"Leave type '{type_name}' added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add leave type: {str(e)}", "danger")

        elif action == 'delete_type':
            type_id = request.form.get('type_id')
            try:
                run_query("DELETE FROM leave_type WHERE type_id = %s;", (type_id,), is_write=True)
                flash("Leave type deleted successfully!", "success")
            except Exception as e:
                flash(f"Cannot delete leave type (may have existing requests): {str(e)}", "danger")

        return redirect(url_for('leaves'))

    _, engine = get_db_connection()
    if engine == 'mysql':
        leave_requests, _ = run_query("""
            SELECT lr.leave_id, e.name AS employee_name, lt.type_name AS leave_type,
                   lr.start_date, lr.end_date, (DATEDIFF(lr.end_date, lr.start_date) + 1) AS num_days,
                   lr.reason, lr.status
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN leave_type lt ON lr.type_id = lt.type_id
            ORDER BY lr.leave_id DESC;
        """)
    else:
        leave_requests, _ = run_query("""
            SELECT lr.leave_id, e.name AS employee_name, lt.type_name AS leave_type,
                   lr.start_date, lr.end_date, CAST(julianday(lr.end_date) - julianday(lr.start_date) + 1 AS INTEGER) AS num_days,
                   lr.reason, lr.status
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN leave_type lt ON lr.type_id = lt.type_id
            ORDER BY lr.leave_id DESC;
        """)

    leave_types, _ = run_query("SELECT type_id, type_name, max_days FROM leave_type;")
    emp_list, _ = run_query("SELECT emp_id, name FROM employee;")
    return render_template('leaves.html', leave_requests=leave_requests, leave_types=leave_types, employees=emp_list)

@app.route('/reports')
def reports():
    _, engine = get_db_connection()

    q1, _ = run_query("""
        SELECT e.name AS employee, d.dept_name AS department, s.shift_name AS shift, s.start_time, s.end_time, sa.work_date
        FROM shift_assignment sa
        JOIN employee e ON e.emp_id = sa.emp_id
        JOIN department d ON d.dept_id = e.dept_id
        JOIN shift s ON s.shift_id = sa.shift_id
        WHERE sa.work_date = '2026-10-05';
    """)

    q2, _ = run_query("SELECT status, COUNT(*) AS total_days FROM attendance GROUP BY status;")

    if engine == 'mysql':
        q3_sql = """
            SELECT e.name AS employee, d.dept_name AS department,
                   SUM(DATEDIFF(lr.end_date, lr.start_date) + 1) AS approved_leave_days
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN department d ON e.dept_id = d.dept_id
            WHERE lr.status = 'Approved'
            GROUP BY e.emp_id, e.name, d.dept_name;
        """
    else:
        q3_sql = """
            SELECT e.name AS employee, d.dept_name AS department,
                   CAST(SUM(julianday(lr.end_date) - julianday(lr.start_date) + 1) AS INTEGER) AS approved_leave_days
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN department d ON e.dept_id = d.dept_id
            WHERE lr.status = 'Approved'
            GROUP BY e.emp_id, e.name, d.dept_name;
        """
    q3, _ = run_query(q3_sql)

    q4, _ = run_query("""
        SELECT d.dept_name, d.location, COUNT(e.emp_id) AS headcount
        FROM department d
        JOIN employee e ON d.dept_id = e.dept_id
        GROUP BY d.dept_id, d.dept_name, d.location
        HAVING COUNT(e.emp_id) >= 2;
    """)

    return render_template('reports.html', q1=q1, q2=q2, q3=q3, q4=q4)

@app.route('/db_settings', methods=['POST'])
def db_settings():
    MYSQL_CONFIG['host'] = request.form.get('host', 'localhost')
    MYSQL_CONFIG['user'] = request.form.get('user', 'root')
    MYSQL_CONFIG['password'] = request.form.get('password', '')
    MYSQL_CONFIG['database'] = request.form.get('database', 'attendance_db')
    MYSQL_CONFIG['port'] = int(request.form.get('port', 3306))

    try:
        import mysql.connector
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        conn.close()
        flash(f"Connected to MySQL database '{MYSQL_CONFIG['database']}' successfully!", "success")
    except Exception as e:
        flash(f"Failed to connect to MySQL ({str(e)}). Using local demo engine.", "warning")

    return redirect(url_for('dashboard'))

@app.route('/audit_logs')
def audit_logs():
    logs, _ = run_query("""
        SELECT al.log_id, au.username, au.full_name, au.role, al.action_type, al.target_table, al.target_id, al.description, al.action_timestamp
        FROM admin_audit_log al
        JOIN admin_user au ON al.admin_id = au.admin_id
        ORDER BY al.log_id DESC;
    """)
    admins, _ = run_query("SELECT * FROM admin_user;")
    return render_template('audit_logs.html', logs=logs, admins=admins)

@app.route('/portal')
@app.route('/admin')
def admin_portal():
    from flask import send_from_directory
    return send_from_directory(os.path.dirname(__file__), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
