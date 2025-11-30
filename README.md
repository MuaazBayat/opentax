![alt text](image.png)

# OpenTax

AI-powered tax assistant built with FastAPI and Next.js.

## Tech Stack

**Backend**
- Python 3.13+
- FastAPI
- SQLAlchemy / SQLModel
- Alembic (migrations)
- Groq (LLM)

**Frontend**
- Next.js 16
- React 19
- Material UI
- Zustand (state management)
- Tailwind CSS

## Project Structure

```
opentax/
├── services/
│   ├── backend/          # FastAPI backend
│   └── frontend/opentax/ # Next.js frontend
├── .github/workflows/    # CI/CD pipelines
├── Makefile              # Development commands
└── repo.secrets          # Local secrets for act (not committed)
```

## Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL (local) or [Neon](https://neon.tech) account
- [act](https://github.com/nektos/act) (for testing GitHub Actions locally)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/opentax.git
cd opentax
```

### 2. Database Setup

**Option A: Neon (Recommended for quick setup)**

1. Create a free account at [neon.tech](https://neon.tech)
2. Create a new project and copy the connection string

**Option B: Local PostgreSQL**

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb opentax
```

### 3. Backend Setup

```bash
# Create environment file
cat > services/backend/.env << 'EOF'
export DATABASE_URL='postgresql://user:password@host:5432/dbname'
export GROQ_API_KEY='your-groq-api-key'
EOF

# Install dependencies
make install-backend
```

### 4. Frontend Setup

```bash
# Install dependencies
make install-frontend
```

## Environment Variables

### Backend (`services/backend/.env`)

```bash
# Database - use Neon or local PostgreSQL
export DATABASE_URL='postgresql://user:password@localhost:5432/opentax'

# Groq API key for LLM
export GROQ_API_KEY='gsk_your_groq_api_key'
```

### Frontend (`services/frontend/opentax/.env.local`)

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Development

### Start both servers

```bash
make dev
```

This runs the backend on http://localhost:8000 and frontend on http://localhost:3000

### Start individually

```bash
make backend   # Backend only
make frontend  # Frontend only
```

### Other commands

```bash
make kill      # Kill processes on ports 8000 and 3000
make clean     # Remove __pycache__, node_modules, .next
make help      # Show all available commands
```

## Testing GitHub Actions Locally with Act

We use [act](https://github.com/nektos/act) to test GitHub Actions workflows locally before pushing.

### Install act

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Setup secrets file

Create a `repo.secrets` file in the project root (already in .gitignore):

```bash
DOCKER_HUB_USERNAME=your_dockerhub_username
DOCKER_HUB_TOKEN=your_dockerhub_token
GCP_CREDENTIALS={"type":"service_account",...}
DATABASE_URL=postgresql://user:pass@host:5432/db
BACKEND_URL=https://your-backend.run.app
```

### Run workflows locally

```bash
# Test frontend CI
make actions-test-frontend-ci

# Test backend CI
make actions-test-backend-ci

# Test backend deployment
make actions-deploy-backend

# Test frontend deployment
make actions-deploy-frontend
```

## Deployment

The project deploys to Google Cloud Run via GitHub Actions when a release is published.

- Backend: `.github/workflows/deploy-backend.yml`
- Frontend: `.github/workflows/deploy-frontend.yml`

