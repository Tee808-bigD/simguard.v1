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
- Frontend on `http://localhost`

### 3. Access the app

Open your browser to:

- Frontend: `http://localhost`
- Backend API docs: `http://localhost:8000/docs`

## Manual Local Run

If you prefer to run the services without Docker:

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host
```

Then open the frontend URL shown by Vite (usually `http://localhost:5173`).

## Notes

- Keep the real `.env` file private.
- `.env.example` contains placeholder values for required API keys and configuration.
- The project uses `docker-compose.yml` to link frontend and backend containers.
