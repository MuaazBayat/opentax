# OpenTax Backend

FastAPI backend service for OpenTax.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Python package manager

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Environment configuration

Create a `.env` file in the backend directory:

```bash
export DATABASE_URL='postgresql://user:password@localhost:5432/opentax'
export GROQ_API_KEY='your-groq-api-key'
```

Source the environment variables before running commands:

```bash
source .env
```

## Database Migrations (Alembic)

### Run migrations

```bash
uv run alembic upgrade head
```

### Create a new migration

```bash
uv run alembic revision --autogenerate -m "description of changes"
```

### View migration history

```bash
uv run alembic history
```

### Downgrade migration

```bash
# Downgrade one step
uv run alembic downgrade -1

# Downgrade to specific revision
uv run alembic downgrade <revision_id>
```

### View current revision

```bash
uv run alembic current
```

## Running the Development Server

```bash
uv run fastapi dev main.py
```

The server will start at `http://localhost:8000`.

API documentation available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`