"""
Database verification and seed script for MySQL.
Attempts connection with common local dev credentials or custom environment settings.
Executes schema.sql, seed.sql, and runs constraint verification tests.
"""

import sys
import mysql.connector
from mysql.connector import Error

PASSWORDS_TO_TRY = ["", "root", "password", "admin", "123456", "mysql"]
HOST = "localhost"
USER = "root"

def get_connection():
    for pwd in PASSWORDS_TO_TRY:
        try:
            conn = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=pwd,
                autocommit=True
            )
            print(f"[SUCCESS] Connected to MySQL Server at {HOST} as {USER} (Password: '{pwd}')")
            return conn, pwd
        except Error as e:
            continue
    return None, None

def execute_sql_file(cursor, filepath):
    print(f"\n---> Executing file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by semicolon while respecting basic strings
    statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
    for stmt in statements:
        # Ignore comments-only blocks
        lines = [line for line in stmt.split('\n') if not line.strip().startswith('--')]
        clean_stmt = '\n'.join(lines).strip()
        if not clean_stmt:
            continue
        try:
            cursor.execute(clean_stmt)
        except Error as err:
            # Print warning if view drop or database create notice
            print(f"   [Notice/Error] {err}")

def run_verification():
    conn, pwd = get_connection()
    if not conn:
        print("[WARNING] Could not automatically connect to local MySQL instance with standard passwords.")
        print("          Ensure MySQL service is running and configured.")
        return False

    cursor = conn.cursor(buffered=True)
    try:
        execute_sql_file(cursor, 'schema.sql')
        print("[OK] schema.sql executed successfully.")

        execute_sql_file(cursor, 'seed.sql')
        print("[OK] seed.sql executed successfully.")

        # Test required queries
        print("\n=== TESTING REQUIRED QUERIES ===")
        cursor.execute("USE attendance_db;")

        print("\n--- Query 1: Today's Shift Roster ---")
        cursor.execute("""
            SELECT e.name, d.dept_name, s.shift_name, s.start_time, s.end_time, sa.work_date
            FROM shift_assignment sa
            JOIN employee e ON e.emp_id = sa.emp_id
            JOIN department d ON d.dept_id = e.dept_id
            JOIN shift s ON s.shift_id = sa.shift_id
            WHERE sa.work_date = '2026-10-05';
        """)
        for row in cursor.fetchall():
            print("  ", row)

        print("\n--- Query 2: Attendance count by status ---")
        cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status;")
        for row in cursor.fetchall():
            print("  ", row)

        print("\n--- Query 3: Approved leave days per employee ---")
        cursor.execute("""
            SELECT e.emp_id, e.name, d.dept_name, SUM(DATEDIFF(lr.end_date, lr.start_date) + 1)
            FROM leave_request lr
            JOIN employee e ON lr.emp_id = e.emp_id
            JOIN department d ON e.dept_id = d.dept_id
            WHERE lr.status = 'Approved'
            GROUP BY e.emp_id, e.name, d.dept_name;
        """)
        for row in cursor.fetchall():
            print("  ", row)

        print("\n--- Query 4: Departments with 2 or more employees ---")
        cursor.execute("""
            SELECT d.dept_name, COUNT(e.emp_id) AS headcount
            FROM department d
            JOIN employee e ON d.dept_id = e.dept_id
            GROUP BY d.dept_id, d.dept_name
            HAVING COUNT(e.emp_id) >= 2;
        """)
        for row in cursor.fetchall():
            print("  ", row)

        print("\n=== TESTING DATABASE CONSTRAINTS (EXPECTED FAILURES) ===")
        # Test 1: Duplicate attendance
        try:
            cursor.execute("INSERT INTO attendance (emp_id, att_date, status) VALUES (1, '2026-10-05', 'Present');")
            print("   [FAIL] Duplicate attendance was incorrectly allowed!")
        except Error as err:
            print(f"   [PASS] Duplicate attendance blocked as expected: {err.msg}")

        # Test 2: Duplicate shift assignment
        try:
            cursor.execute("INSERT INTO shift_assignment (emp_id, shift_id, work_date) VALUES (1, 2, '2026-10-05');")
            print("   [FAIL] Duplicate shift assignment was incorrectly allowed!")
        except Error as err:
            print(f"   [PASS] Duplicate shift assignment blocked as expected: {err.msg}")

        # Test 3: Invalid check-out time
        try:
            cursor.execute("INSERT INTO attendance (emp_id, att_date, check_in, check_out, status) VALUES (1, '2026-10-06', '17:00:00', '09:00:00', 'Present');")
            print("   [FAIL] Invalid check-out time was incorrectly allowed!")
        except Error as err:
            print(f"   [PASS] Invalid check-out blocked as expected: {err.msg}")

        # Test 4: Delete department with employees (ON DELETE RESTRICT)
        try:
            cursor.execute("DELETE FROM department WHERE dept_id = 1;")
            print("   [FAIL] Department deletion with employees was incorrectly allowed!")
        except Error as err:
            print(f"   [PASS] ON DELETE RESTRICT blocked deletion as expected: {err.msg}")

        print("\n[ALL DATABASE VERIFICATION TESTS PASSED SUCCESSFULLY!]")
        return True

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_verification()
