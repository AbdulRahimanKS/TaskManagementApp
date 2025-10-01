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
git clone <GITHUB_LINK_HERE>
cd <REPO_FOLDER>
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

Since the database is pushed, you can use the existing credentials:

* **Superadmin:** superadmin@noviindus.com / SuperAdmin123
* **Admin:** [admin@example.com](mailto:admin@example.com) / password123
* **User:** [user@example.com](mailto:user@example.com) / password123
