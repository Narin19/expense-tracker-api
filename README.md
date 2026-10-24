# Expense Tracker API

A FastAPI backend using PostgreSQL for managing expenses and user authentication.

## Requirements

- Python installed
- PostgreSQL installed and running
- A PostgreSQL database created for this project

## 1. Clone or download the project

Open a terminal in the project folder.

## 2. Create a virtual environment

```powershell
python -m venv .venv
```

## 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 5. Configure environment variables

Set `DATABASE_URL` to your own PostgreSQL connection URL. Configure any required authentication secrets as well. Never share your personal database password.

## 6. Start the API

```powershell
python -m uvicorn main:app --reload
```

## 7. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

Use Swagger UI to test the API endpoints.

## Run automated tests

Configure `TEST_DATABASE_URL` to point to a separate test database, then run:

```powershell
python -m pytest -v
```
