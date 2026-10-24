# Expense Tracker API

A RESTful backend application built with **FastAPI** and **PostgreSQL** for user authentication and expense management. It includes JWT-based authentication, password hashing, user-specific expense access, and automated tests.

## Features

- User registration and login
- JWT-based authentication
- Secure password hashing
- Create, read, update, and delete expenses
- User-specific expense access
- Input validation and error handling
- PostgreSQL database integration
- Interactive API documentation with Swagger UI
- Automated tests using Pytest

## Tech Stack

- **Language:** Python
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Password hashing:** pwdlib
- **Testing:** Pytest, FastAPI TestClient

## Prerequisites

- Python installed
- PostgreSQL installed and running
- Git installed
- A PostgreSQL database for the application
- A separate PostgreSQL database for testing

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Narin19/expense-tracker-api.git
cd expense-tracker-api
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Add your own PostgreSQL credentials and a strong, randomly generated JWT secret.

```dotenv
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/expense_tracker
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/expense_tracker_test
SECRET_KEY=YOUR_LONG_RANDOM_SECRET
```

Replace the example values with your own settings. URL-encode special characters in your PostgreSQL password when necessary.

**Security:** Never commit or share your `.env` file. Keep your test database separate from your application database.

### 5. Initialize the database

Make sure PostgreSQL is running and that the database specified by `DATABASE_URL` already exists.

Run the following command from the project root to create the required tables:

```powershell
python database.py
```

This creates the `users` and `expenses` tables if they do not already exist.

### 6. Start the API

```powershell
python -m uvicorn main:app --reload
```

### 7. Open the API documentation

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and test the API endpoints.


## Running Tests

Configure `TEST_DATABASE_URL` to point to your separate test database, then run:

```powershell
python -m pytest -v
```

The project has **9 automated tests passing** in the current development environment.

## Repository

[GitHub: Narin19/expense-tracker-api](https://github.com/Narin19/expense-tracker-api)
