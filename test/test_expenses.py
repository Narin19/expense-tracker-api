
from uuid import uuid4


def create_test_user(client):
    email = f"{uuid4().hex}@example.com"
    password = "TestPass123!"

    signup = client.post(
        "/users/signup",
        json={
            "name": "Test User",
            "email": email,
            "password": password
        }
    )
    assert signup.status_code == 201

    login = client.post(
        "/users/login",
        json={"email": email, "password": password}
    )
    assert login.status_code == 200

    return login.json()["access_token"]


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Expense Tracker API is running"
    }


def test_expenses_without_token(client):
    response = client.get("/expenses")
    assert response.status_code == 401


def test_expenses_with_invalid_token(client):
    response = client.get(
        "/expenses",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


def test_signup(client):
    email = f"{uuid4().hex}@example.com"

    response = client.post(
        "/users/signup",
        json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "access_token" not in response.json()


def test_duplicate_signup(client):
    email = f"{uuid4().hex}@example.com"
    payload = {
        "name": "Test User",
        "email": email,
        "password": "TestPass123!"
    }

    first_response = client.post("/users/signup", json=payload)
    second_response = client.post("/users/signup", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_success(client):
    email = f"{uuid4().hex}@example.com"
    password = "TestPass123!"

    signup_response = client.post(
        "/users/signup",
        json={
            "name": "Login Tester",
            "email": email,
            "password": password
        }
    )
    assert signup_response.status_code == 201

    response = client.post(
        "/users/login",
        json={"email": email, "password": password}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)
    assert len(response.json()["access_token"]) > 0


def test_login_wrong_password(client):
    email = f"{uuid4().hex}@example.com"

    signup_response = client.post(
        "/users/signup",
        json={
            "name": "Login Tester",
            "email": email,
            "password": "TestPass123!"
        }
    )
    assert signup_response.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": email,
            "password": "WrongPass123!"
        }
    )

    assert response.status_code == 401


def test_user_cannot_update_another_users_expense(client):
    owner_token = create_test_user(client)
    other_token = create_test_user(client)

    create_response = client.post(
        "/expenses",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Private expense",
            "amount": 500,
            "category": "Food"
        }
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    update_response = client.put(
        f"/update/expenses/{expense_id}/1000",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert update_response.status_code == 404

    owner_expenses = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert owner_expenses.status_code == 200

    expense = next(
        item for item in owner_expenses.json()["expenses"]
        if item["id"] == expense_id
    )
    assert expense["amount"] == 500


def test_user_cannot_delete_another_users_expense(client):
    owner_token = create_test_user(client)
    other_token = create_test_user(client)

    create_response = client.post(
        "/expenses",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Private expense",
            "amount": 500,
            "category": "Food"
        }
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert delete_response.status_code == 404

    owner_expenses = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert owner_expenses.status_code == 200

    expense_ids = [
        item["id"] for item in owner_expenses.json()["expenses"]
    ]
    assert expense_id in expense_ids
