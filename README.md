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

- Employee information
- Department information
- Work shifts
- Employee shift assignments
- Daily attendance
- Leave types
- Employee leave requests
- Leave approval and rejection
- SQL-based reports

The project demonstrates how a relational database can be integrated with a web application to solve a practical organizational problem.

The application provides an administrative interface where users can view and manage employee records, departments, shifts, attendance and leave requests. It also provides reporting functionality using SQL queries.

---

# 🎯 Project Objectives

The main objectives of this project are:

1. To create a centralized employee management database.
2. To maintain department and employee information.
3. To manage multiple employee work shifts.
4. To assign shifts to employees for specific dates.
5. To record daily employee attendance.
6. To manage different types of employee leave.
7. To allow leave requests to be approved or rejected.
8. To prevent duplicate and invalid database records.
9. To generate useful reports using SQL.
10. To demonstrate practical DBMS concepts using MySQL and Python Flask.

---

# ✨ Features & Functionalities

## 👥 Employee Management

The employee management module stores important employee information such as:

- Employee ID
- Employee name
- Email
- Phone number
- Hire date
- Department

The system maintains a relationship between employees and departments using a foreign key.

Employee email addresses are also maintained as unique values to reduce duplicate employee records.

---

## 🏢 Department Management

The department module allows the system to maintain organizational departments.

Each department contains:

- Department ID
- Department name
- Location

The sample project contains:

```text
HR
IT
Finance
Sales
Operations
