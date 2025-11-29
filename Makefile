.PHONY: help backend frontend dev install-backend install-frontend install clean kill

# Default target
help:
	@echo "OpenTax Development Commands"
	@echo "============================"
	@echo "make dev              - Start both backend and frontend servers"
	@echo "make backend          - Start backend server only"
	@echo "make frontend         - Start frontend server only"
	@echo "make kill             - Kill processes on ports 8000 and 3000"
	@echo "make install          - Install all dependencies"
	@echo "make install-backend  - Install backend dependencies"
	@echo "make install-frontend - Install frontend dependencies"
	@echo "make clean            - Clean up __pycache__ and node_modules"

# Start both servers in parallel
dev:
	@echo "Starting OpenTax servers..."
	@make -j2 backend frontend

# Start backend server
backend:
	@echo "Starting backend server on http://localhost:8000"
	@cd services/backend && source .env && source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend server
frontend:
	@echo "Starting frontend server on http://localhost:3000"
	@cd services/frontend/opentax && npm run dev

# Install all dependencies
install: install-backend install-frontend
	@echo "All dependencies installed!"

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	@cd services/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Install frontend dependencies
install-frontend:
	@echo "Installing frontend dependencies..."
	@cd services/frontend/opentax && npm install

# Kill processes on backend and frontend ports
kill:
	@echo "Killing processes on ports 8000 and 3000..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process on port 8000"
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No process on port 3000"
	@echo "Ports cleared!"

actions-test-frontend-ci:
	act -W '.github/workflows/frontend-ci.yml' --secret-file repo.secrets --container-architecture=linux/amd64

actions-test-backend-ci:
	act -W '.github/workflows/backend-ci.yml' --secret-file repo.secrets --container-architecture=linux/amd64

actions-deploy-backend:
	act -W '.github/workflows/deploy-backend.yml' --secret-file repo.secrets --container-architecture=linux/amd64

actions-deploy-frontend:
	act -W '.github/workflows/deploy-frontend.yml' --secret-file repo.secrets --container-architecture=linux/amd64

# Clean up
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"