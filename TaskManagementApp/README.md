"# TaskManagementApp" 

Task Management System
Overview
This project is a Task Management System designed to facilitate the assignment, tracking, and reporting of tasks. The system supports role-based functionality, including Users, Admins, and SuperAdmins, with secure authentication via JWT tokens.

Features
User Features:
Authenticate via JWT tokens using username and password.

View assigned tasks.

Update task status (e.g., mark as completed) and provide a completion report.

Admin Features:
View tasks created by the admin.

Monitor pending, in-progress, and completed tasks.

Assign tasks to users.

Remove users from tasks.

SuperAdmin Features:
Manage admins and users.

View task reports for all tasks.

Setup Instructions
Prerequisites
Python 3.8+

Django 4.2+

A virtual environment tool like venv or virtualenv

Postman (optional, for testing APIs)

Installation
Clone the repository:

git clone https://github.com/abhinandbhaskar/TaskManagementApp.git

cd TaskManagementApp

python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

This script simplifies the process of creating default admin and superadmin accounts for the application.

The create_users function initializes a superadmin and an admin with predefined credentials, while the helper functions create_superadmin and create_admin ensure that these accounts are created only if they don't already exist in the database. This is useful for quickly setting up roles during development or testing.