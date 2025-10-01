# Task Management Application

This is a **Task Management Application** built using **Python 3.12** and  **Django**. It allows managing users, admins, tasks, and task completion reports. Admins and Superadmins can track completed tasks, worked hours, and completion reports. Users can update task completion via APIs.

---

## Features

* JWT-based authentication for users
* Role-based access: User, Admin, Superadmin
* Task creation, assignment, and status updates
* Task completion reports and worked hours tracking
* Admin panel to manage tasks and users
* Swagger API documentation

---

## Prerequisites

* Python 3.12
* Git
* Virtual environment tool (`venv` or `virtualenv`)

---

## Installation & Setup

1. **Clone the repository**

```bash
git clone https://github.com/AbdulRahimanKS/TaskManagementApp.git
cd TaskManagementApp
```

2. **Create a virtual environment**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

* **Windows**

```bash
venv\Scripts\activate
```

* **Linux / Mac**

```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Run the Django server**

```bash
python manage.py runserver
```

---

## Accessing the Application

* Application URL (local server):

```
http://127.0.0.1:8000/
```

* Swagger API documentation:

```
http://127.0.0.1:8000/api/schema/swagger_docs/
```

---

## Credentials

Since the database is pushed, you can use some of the existing credentials:

* **Superadmin:** superadmin@noviindus.com / SuperAdmin123
* **Admin:** adminuser1@noviindus.com / AdminUser1123
* **User:** user1@noviindus.com / User1123

---

## API Endpoints

### User Authentication

* **POST /api/v1/Login/** : Users authenticate with email and password and receive a JWT token for further requests.

### Tasks APIs

* **GET api/v1/tasks/** : Fetch all tasks assigned to the user.
* **PUT api/v1/tasks/{id}/** : Update the status of a task (mark as Completed).
  * When marking a task as Completed, users must submit a Completion Report and Worked Hours.
* **GET api/v1/tasks/{id}/report/** : Admins and SuperAdmins can view the Completion Report and Worked Hours for a specific task.
  * Only available for tasks that are marked as Completed.

---

## Admin Panel

### Manage Users (Superadmin only)

* Only accessible by the Superadmin.
* Create users and assign roles (Admin or User).
* Update users to promote or demote roles.
* Assign users (role: User) to an Admin.
* Admin users can only see the users assigned to them; they cannot manage users.

### Manage Tasks (Admin & Superadmin)

* Both Admin and Superadmin can manage tasks.
* Update task status in the task edit section.
* When marking a task as Completed, working hours and a completion report must be submitted.

### Task Reports (Admin & Superadmin)

* View a list of all completed tasks.
* See task completion reports and worked hours details.
