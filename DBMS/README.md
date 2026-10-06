# Employee Attendance, Shift & Leave Management System

A production-grade, 3NF normalized MySQL database system and interactive Python Flask web application designed for employee tracking, multi-shift scheduling, attendance logging, and leave management.

---

## 📋 Features & Functionalities

- **AI Shift Engine & User Change Controls:** AI automatically assigns smart rotational shifts to employees; Managers/Users can manually change any shift at any time.
- **1-Click Attendance Logger:** Quick 1-click attendance recording (`Present`, `Late`, `Absent`) with custom date pickers per row.
- **Leave Management:** Support for leave types (`max_days > 0`), employee leave applications (`end_date >= start_date`), and HR approval workflows.
- **Relational Integrity:** `ON DELETE RESTRICT` on departments, `UNIQUE(emp_id, work_date)`, `UNIQUE(emp_id, att_date)`.

---

## ⚙️ Quick Setup & Execution

### 1. Execute SQL in MySQL Workbench / CLI

```sql
mysql -u root -p

-- Execute schema, seed data, and analytical queries:
SOURCE c:/Users/Sys/OneDrive/Desktop/project/DBMS/schema.sql;
SOURCE c:/Users/Sys/OneDrive/Desktop/project/DBMS/seed.sql;
SOURCE c:/Users/Sys/OneDrive/Desktop/project/DBMS/queries.sql;
```

---

### 2. Launch the Web Application

```bash
python app.py
```

Open **`http://127.0.0.1:5000`** in your browser.
