
import os
from datetime import datetime, timedelta, timezone

import jwt
import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from dotenv import load_dotenv

from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

bearer_scheme = HTTPBearer()
password_hash = PasswordHash.recommended()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Add it to your .env file."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign(
    user: SignupRequest,
    connection: psycopg.Connection = Depends(get_db)
):
    existing_user = connection.execute(
        "SELECT id FROM users WHERE email = %s",
        (str(user.email),)
    ).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(user.password)

    cursor = connection.execute(
        """
        INSERT INTO users (name, email, hashed_password)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (user.name, str(user.email), hashed_password)
    )

    new_user = cursor.fetchone()
    connection.commit()

    return {
        "message": "User registered successfully",
        "id": new_user["id"],
        "name": user.name,
        "email": str(user.email)
    }


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(
    user: LoginRequest,
    connection: psycopg.Connection = Depends(get_db)
):
    existing_user = connection.execute(
        """
        SELECT id, email, hashed_password
        FROM users
        WHERE email = %s
        """,
        (str(user.email),)
    ).fetchone()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        user.password, existing_user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {"sub": str(existing_user["id"])}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    connection: psycopg.Connection = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = connection.execute(
        "SELECT id, name, email FROM users WHERE id = %s",
        (user_id,)
    ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return dict(user)
