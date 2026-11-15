# Revision Token & Scope-Creep Shield

A freelance project management backend built with FastAPI, SQLAlchemy, and SQLite.

## Features

- User registration and authentication
- JWT-based authentication and role-based access
- Freelancer project management
- Milestone management
- Three free revision tokens per milestone
- Automatic token deduction by the backend
- Add-on revision requests after free tokens are exhausted
- Add-on quote creation and client approval/rejection
- Project activity tracking
- Notifications for revision and quote events
- Database health checks

## Technology Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Pytest
- Alembic

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
```

Before running the application, replace the example `SECRET_KEY` and freelancer invitation code in `.env` with private values.

## Start Backend

```bash
python3 -m uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

## API Endpoints

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a client |
| POST | `/auth/login` | Log in and receive JWT |
| GET | `/auth/me` | Get current user |
| POST | `/auth/register-freelancer` | Register a freelancer |

### Projects

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/projects/` | Create a project |
| GET | `/projects/` | List accessible projects |
| GET | `/projects/{project_id}` | Get project details |

### Milestones

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/projects/{project_id}/milestones/` | Create a milestone |
| GET | `/projects/{project_id}/milestones/` | List project milestones |

### Revisions

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/projects/{project_id}/milestones/{milestone_id}/revisions/` | Submit a revision request |

### Quotes

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/projects/{project_id}/quotes/{revision_id}` | Create an add-on quote |
| GET | `/projects/{project_id}/quotes/` | List project quotes |
| PATCH | `/projects/{project_id}/quotes/{quote_id}/status` | Accept or reject a quote |

### Activity and Notifications

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/projects/{project_id}/activity/` | View project activity |
| GET | `/notifications/` | Get current user's notifications |
| PATCH | `/notifications/{notification_id}/read` | Mark notification as read |

### System

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome endpoint |
| GET | `/health` | Application and database health |

## Revision Token Rules

- Every new milestone starts with three free revision tokens.
- Each free revision consumes one token.
- Once all three tokens are used, further revision requests become `ADD_ON`.
- Add-on revisions require a quote.
- Quotes begin with `PENDING` status.
- Clients can `ACCEPT` or `REJECT` quotes.

**Important:** The backend is responsible for token deduction. The frontend must never independently deduct tokens.

## Authentication

Protected endpoints require a JWT access token.

1. Register or log in.
2. Obtain the access token from the login response.
3. Send the token in the request header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The login endpoint accepts form data with `username` (the registered email) and `password`.

## Frontend Integration

- Backend base URL: `http://127.0.0.1:8000`
- API documentation: `http://127.0.0.1:8000/docs`
- Use the login endpoint to authenticate users.
- Include the JWT bearer token in protected requests.
- Display the token balance returned by the backend.
- Do not implement token deduction in the frontend.
- Use the notifications endpoint to display user notifications.

## Database

SQLite is the default database.

Configure `DATABASE_URL` in `.env` to use another supported database.

## Testing

Run the automated test suite:

```bash
python3 -m pytest -v
```

Current test result: 19 passed.

## Team Integration

The backend provides the API and business logic for the frontend. The frontend team should use the documented endpoints and Swagger UI to understand request and response schemas.

The database and token logic must remain controlled by the backend.
