# Secure Campus Communication System

A full-stack Flask web application for secure messaging between Campus A and Campus B.

## Features

- User registration with campus assignment (A or B)
- bcrypt password hashing
- Session-based authentication via Flask-Login
- Role-based access (user / admin)
- Secure messaging between any two users
- HTTPS via Flask adhoc SSL certificate
- Auto-refreshing message history (every 15 s)
- Default admin account for oversight

## Project Structure

```
secure-campus-comm/
├── app.py            # App factory & entry point
├── extensions.py     # Shared db + login_manager
├── models.py         # User & Message ORM models
├── auth.py           # /register  /login  /logout
├── messages.py       # /send-message  /get-messages  /get-users
├── views.py          # HTML page routes
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Setup & Run

### 1. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

The app starts on **https://localhost:5000**

> Your browser will show a certificate warning because the SSL cert is self-signed (adhoc). Click "Advanced → Proceed" to continue.

## Default Admin Account

| Field    | Value    |
|----------|----------|
| Username | admin    |
| Password | admin123 |
| Campus   | A        |
| Role     | admin    |

Change the admin password after first login.

## REST API Endpoints

| Method | Endpoint        | Auth required | Description                  |
|--------|-----------------|---------------|------------------------------|
| POST   | /register       | No            | Register a new user          |
| POST   | /login          | No            | Login and start session      |
| GET    | /logout         | Yes           | End session                  |
| POST   | /send-message   | Yes           | Send a message               |
| GET    | /get-messages   | Yes           | Fetch messages (own or all)  |
| GET    | /get-users      | Yes           | List all other users         |
| GET    | /dashboard      | Yes           | Dashboard HTML page          |

All endpoints accept and return JSON when the `Content-Type: application/json` header is set.

## Security Notes

- Passwords are hashed with bcrypt (cost factor 12)
- Sessions are server-side via Flask-Login
- All traffic is encrypted over HTTPS
- Input is validated on both client and server
- XSS is prevented via Jinja2 auto-escaping and JS `escapeHtml()`
- For production: replace `SECRET_KEY`, use a real TLS certificate, and switch to PostgreSQL/MySQL
