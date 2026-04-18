# SimGuard

SimGuard is a fraud detection and verification dashboard built with a FastAPI backend and a React/Vite frontend.

## Quick Start

### 1. Copy environment variables

Create a local environment file from the example:

```powershell
copy .env.example .env
```

### 2. Start with Docker Compose

Use the Docker Compose setup to build and run both services:

```powershell
docker compose up --build
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:5173/`

### 3. Access the app

Open your browser to:

- Frontend: `http://localhost:5173/`
- Backend API docs: `http://localhost:8000/docs`

## Manual Local Run

If you prefer to run the services without Docker:

### Backend

```powershell
cd backend
C:\Users\Thando\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv httpx
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host
```

Then open the frontend URL shown by Vite (usually `http://localhost:5173`).

## Deployment

The application can be deployed with Docker Compose or any container platform that supports separate backend and frontend services.

- Build and run locally with `docker compose up --build`
- Host the backend on any platform that supports FastAPI/Uvicorn and a SQLite or compatible database
- Host the frontend as a static site behind Nginx or another web server, pointing the API base URL to the backend

### GitHub Actions (optional)

A simple CI workflow can install dependencies and validate the project files before deployment.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install backend dependencies
        run: |
          cd backend
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
      - name: Check frontend install
        run: |
          cd frontend
          npm install
```

## Notes

- Keep the real `.env` file private.
- `.env.example` contains placeholder values for required API keys and configuration.
- The project uses `docker-compose.yml` to link frontend and backend containers.
