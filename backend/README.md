# Depo Audio OS - Backend

FastAPI backend service for Depo Audio OS (Automotive Lighting Workshop Operating System).

## Running the Backend Locally

### 1. Prerequisites
- Python 3.8+ (with `venv` support)
- PowerShell (Windows) or Bash (macOS/Linux)

### 2. Virtual Environment Setup

#### Windows (PowerShell):
```powershell
# Navigate to the backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the `.env.example` file to `.env`:
```powershell
# Windows
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```
Fill in your local or development Supabase credentials in `.env`:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service-role secret key
- `SUPABASE_JWT_SECRET`: Secret for verifying JWTs (used in future auth middleware)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins (defaults to `http://localhost:5173`)

> **Important**: Never commit `.env` to version control. It is ignored in `.gitignore`.

### 5. Start the Development Server
With your virtual environment activated:
```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Verify Health Check
Open your browser or run:
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "ok"}
```

API documentation is also available locally at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).
