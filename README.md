# Course Management System
This project is a Python-based application designed to manage a course registration system. It allows students to view courses, enroll or withdraw from courses, and manage their enrollments. Professors can also view their teaching assignments.

Features
Student Operations:

View all available courses.
Enroll in or withdraw from courses.
Search for courses by name.
View current enrollments.
Check prerequisites for specific courses.
Professor Operations:

View information about courses being taught and total credits.
Database Integration:

Connects to a MySQL database to manage data for students, courses, enrollments, schedules, prerequisites, and professors.
File Descriptions
courseManagmentSystemGROUP4.py
This is the main script that implements the course management system. It includes the following key functionalities:

Database connection and operations using MySQL.
Commands for managing student enrollments and professor teaching assignments.
User-friendly command-line interface with a help menu.
Installation
Requirements
Python 3.x
MySQL database
mysql-connector library (install via pip install mysql-connector-python)
Setup
Clone or download the project files.

Install the required Python library:

bash
Copy code
pip install mysql-connector-python
Configure the MySQL database with the following credentials:


Populate the database with the necessary tables and data (e.g., Students, Courses, Enrolled, Schedules, Prerequisites, Teaching, and Professor).

Usage
Run the program:

bash
Copy code
python courseManagmentSystemGROUP4.py
Follow the prompts to log in as a student or sign up for a new account.

Use the following commands:

L - List all available courses.
E - Enroll in a course.
W - Withdraw from a course.
S - Search for a course by name.
M - View your current enrollments.
P - Check prerequisites for a course.
T - View professor teaching assignments.
H - Display help menu.
X - Exit the program.
