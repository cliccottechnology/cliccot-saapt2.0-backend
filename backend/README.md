# Django Authentication Backend (JWT + REST Framework)

Production-ready Django REST Framework backend for user registration, authentication (JWT), profile management, and logout.

---

## 🚀 Features

- **Custom User Model**: Inherits from `AbstractUser` with unique email enforcement and custom fields.
- **JWT Authentication**: Uses `djangorestframework-simplejwt` for secure access and refresh token handling.
- **Flexible Login**: Allows users to log in using **either their username or their email address**.
- **Instant Login on Register**: Registration automatically returns JWT tokens so the user is immediately authenticated.
- **Token Blacklisting on Logout**: Invalidate refresh tokens on logout for heightened security.
- **CORS Configured**: Pre-configured with `django-cors-headers` for seamless integration with frontend frameworks (React, Vue, Next.js, Flutter, etc.).
- **Password Strength Validation**: Django's built-in password validators enforce strong passwords.
- **Unit Tested**: Full test suite verifying registration, dual-identifier login, profile access, and validation rules.

---

## 📁 Project Structure

```text
SAAPT 2.0/
├── accounts/
│   ├── migrations/
│   ├── admin.py          # Django admin configuration
│   ├── apps.py
│   ├── models.py         # CustomUser model
│   ├── serializers.py    # Register, Login, Profile & Password serializers
│   ├── tests.py          # Automated test suite
│   ├── urls.py           # Authentication routes
│   └── views.py          # API endpoints
├── core/
│   ├── asgi.py
│   ├── settings.py       # DRF, SimpleJWT, CORS & DB settings
│   ├── urls.py           # Main routing
│   └── wsgi.py
├── .env.example          # Environment variables template
├── .env                  # Local environment file
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Quick Start

### 1. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 2. Run Database Migrations (Already configured)

```bash
python manage.py migrate
```

### 3. Create Superuser (Optional, for Django Admin)

```bash
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

The server will be running at `http://127.0.0.1:8000/`.

### 5. Run Tests

```bash
python manage.py test
```

---

## 📡 API Endpoints Reference

Base URL: `http://127.0.0.1:8000/api/auth/`

| Endpoint | Method | Auth Required | Description |
| :--- | :---: | :---: | :--- |
| `/api/auth/register/` | `POST` | No | Register a new user and receive JWT tokens |
| `/api/auth/login/` | `POST` | No | Log in via username OR email & receive JWT tokens |
| `/api/auth/token/refresh/` | `POST` | No | Refresh an expired access token |
| `/api/auth/me/` | `GET`, `PUT`, `PATCH` | **Yes (Bearer Token)** | View or update current user profile |
| `/api/auth/logout/` | `POST` | **Yes (Bearer Token)** | Invalidate/blacklist refresh token |
| `/api/auth/change-password/` | `POST` | **Yes (Bearer Token)** | Update user password |

---

## 📝 API Request & Response Examples

### 1. Register User

- **URL:** `POST /api/auth/register/`
- **Request Body:**
```json
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "password": "StrongPassword123!",
  "confirm_password": "StrongPassword123!"
}
```

- **Response (`201 Created`):**
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "created_at": "2026-10-15T12:00:00Z",
    "updated_at": "2026-10-15T12:00:00Z"
  },
  "tokens": {
    "refresh": "<jwt_refresh_token>",
    "access": "<jwt_access_token>"
  }
}
```

---

### 2. Login User

- **URL:** `POST /api/auth/login/`
- **Request Body (Login via Username OR Email):**
```json
{
  "username_or_email": "johndoe@example.com",
  "password": "StrongPassword123!"
}
```

- **Response (`200 OK`):**
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "created_at": "2026-10-15T12:00:00Z",
    "updated_at": "2026-10-15T12:00:00Z"
  },
  "tokens": {
    "refresh": "<jwt_refresh_token>",
    "access": "<jwt_access_token>"
  }
}
```

---

### 3. Access Protected Route (Current User Profile)

- **URL:** `GET /api/auth/me/`
- **Headers:**
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **Response (`200 OK`):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "johndoe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "created_at": "2026-10-15T12:00:00Z",
  "updated_at": "2026-10-15T12:00:00Z"
}
```

---

### 4. Refresh Token

- **URL:** `POST /api/auth/token/refresh/`
- **Request Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```
- **Response (`200 OK`):**
```json
{
  "access": "<new_jwt_access_token>",
  "refresh": "<new_jwt_refresh_token>"
}
```

---

### 5. Logout

- **URL:** `POST /api/auth/logout/`
- **Headers:**
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **Request Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```
- **Response (`200 OK`):**
```json
{
  "message": "Logged out successfully."
}
```
