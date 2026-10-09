# Employee Attendance, Shift & Leave Management System

A production-grade **3NF-normalized MySQL database system** with an interactive **Python Flask web application** designed to manage employee information, departments, work shifts, shift assignments, attendance records, and leave requests in a centralized system.

---

# 👥 Project Team

## 📌 Project Name
### Employee Attendance, Shift & Leave Management System

## 👨‍💻 Team Members

| S. No. | Name | Roll Number |
|---:|---|---|
| 1 | **V. Sathwik** | **25WU0102302** |
| 2 | **Y. Aditya Sreekar** | **25WU0102303** |
| 3 | **Vinti Satya Rohan** | **25WU0102300** |

### 🎓 Academic Details

- **University:** Woxsen University
- **School:** School of Technology
- **Course:** Database Management System (DBMS)
- **Semester:** III
- **Academic Year:** 2025–29
- **Faculty:** Dr. Kiran Mayee

---

# 📖 About This Project

The **Employee Attendance, Shift & Leave Management System** is a database-driven web application developed to manage employee-related information and daily organizational operations through a centralized system.

The project combines a **MySQL relational database** with a **Python Flask web application**. The database is designed using **Third Normal Form (3NF)** principles to reduce data redundancy, improve consistency, and maintain relationships between different types of employee information.

The system manages:
- Employee information & Department hierarchy
- Multi-shift scheduling & Rotational shift assignments
- Daily attendance logging with status tracking
- Leave categories, policies, and leave requests workflow
- Administrative roles (`Super Admin`, `HR Admin`, `Operations Admin`)
- Immutable security audit logs (`admin_audit_log`)
- SQL-based analytical views and reports

---

# 🎯 Project Objectives

1. To create a centralized employee management database in Third Normal Form (3NF).
2. To maintain department and employee relationships with referential integrity (`ON DELETE RESTRICT`).
3. To manage multiple work shifts and rotational schedules.
4. To assign shifts to employees for specific dates without scheduling conflicts (`UNIQUE(emp_id, work_date)`).
5. To record daily employee attendance with 1-click status updates (`UNIQUE(emp_id, att_date)`).
6. To enforce leave policies and leave allowances (`max_days > 0`).
7. To provide 1-click approval/rejection workflows for leave requests (`end_date >= start_date`).
8. To track all administrative modifications via immutable audit logging.
9. To demonstrate practical DBMS concepts using MySQL, Python Flask, and modern web UI.

---

# ✨ Features & Functionalities

- **Enterprise Admin Interface:** Centralized control center with role-based access (`Super Admin`, `HR Admin`, `Operations Admin`), immutable security audit trail (`admin_audit_log`), and live DBMS SQL console.
- **Smart Shift Engine & User Change Controls:** Automatic assignment of rotational shifts to employees; Admins can manually update or reassign shifts at any time.
- **1-Click Attendance Logger:** Quick attendance recording (`Present`, `Late`, `Absent`, `Half-day`) with custom date pickers per record.
- **Leave Management:** Custom leave categories, balance tracking, and 1-click approval/rejection workflows.
- **Relational Integrity:** Foreign key constraints, cascade updates, check constraints, and unique compound keys across all tables.

---

# 🔑 Default Administrator Credentials

| Username | Password | Full Name | System Role | Email |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin123` | System Administrator | **Super Admin** | `admin@attendx.com` |
| `priya_hr` | `hrpass123` | Priya Sharma | **HR Admin** | `priya.hr@attendx.com` |
| `karthik_ops` | `opspass123` | Karthik Verma | **Operations Admin** | `karthik.ops@attendx.com` |

---

# ⚙️ Quick Setup & Execution

All source code and database scripts are located in the **[`sourcecode/`](file:///c:/Users/Sys/OneDrive/Desktop/project/DBMS/sourcecode)** directory.

### Option A: Launch Standalone Admin Portal (Zero Dependencies)
Open **`sourcecode/index.html`** in any modern web browser. It runs a complete in-memory 3NF relational engine with live interactive CRUD for employees/departments, shift roster, leave approvals, and SQL console.

### Option B: Execute SQL in MySQL Workbench / CLI

```sql
mysql -u root -p

-- Execute unified database script:
SOURCE sourcecode/database.sql;

-- Or execute modular scripts:
SOURCE sourcecode/schema.sql;
SOURCE sourcecode/seed.sql;
SOURCE sourcecode/queries.sql;
```

---

### Option C: Launch Flask Web Application

```bash
cd sourcecode
python app.py
```

Open **`http://127.0.0.1:5000`** in your browser.
