# Family Tree Backend API

A production-ready FastAPI backend for managing family groups and their biological family trees.

## Features

- **Authentication**: JWT-based login and registration.
- **Family Groups**: Users can create, join, and manage family groups.
- **Invitations**: Invite users via email to join a group with specific roles.
- **Roles & Permissions**:
  - `CREATOR`: Full access, can promote members.
  - `ADMIN`: Can add/edit family tree members and relationships.
  - `MEMBER`: View-only access with ability to comment.
- **Family Tree**: Biological relationships (Parent-Child, Partners) that support computing siblings, ancestors, etc.
- **Comments**: Activity log for tree members.
- **Tech Stack**: FastAPI, SQLModel (ORM), PostgreSQL, Alembic (Migrations), Docker.

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Running the App

1. Clone the repository (if applicable) and navigate to the project directory.
2. Build and start the services:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`.
4. Interactive Swagger documentation: `http://localhost:8000/docs`.

---

## Example API Flow (Postman/Curl)

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword", "full_name": "Juan Perez"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -d "username=user@example.com&password=securepassword"
```

### 3. Create a Family Group
```bash
curl -X POST "http://localhost:8000/api/v1/groups/" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "The Perez Family", "description": "Ancestors of Juan Perez"}'
```

### 4. Create a Tree Member
```bash
curl -X POST "http://localhost:8000/api/v1/groups/1/members" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Pedro", "last_name": "Perez", "birth_date": "1950-01-01", "gender": "MALE"}'
```

---

## Project Structure

```text
├── alembic/              # Database migration scripts
├── app/                  # Application source
│   ├── api/              # API endpoints logic
│   ├── core/             # Auth, Settings, Security
│   ├── db/               # DB Session manager
│   ├── models/           # SQLModel domain models
│   ├── schemas/          # Pydantic schemas (DTOs)
│   └── main.py           # App entry point
├── Dockerfile            # Backend Docker image
├── docker-compose.yml    # Full stack orchestration
└── requirements.txt      # Python dependencies
```

---

## Database Migrations

To apply or generate migrations inside the container:

```bash
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
```

Note: Tables are automatically created during the first run for convenience.
