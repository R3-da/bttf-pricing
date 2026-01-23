# Local Development Setup

To run the application with a local PostgreSQL database running in Docker:

## 1. Start the Infrastructure
Run Docker Compose to start the PostgreSQL database and pgAdmin:
```bash
docker compose up -d
```

## 2. Environment Setup
Ensure you are in the project root and have your virtual environment activated:
```bash
# Example using venv
source .venv/bin/activate
# Install dependencies (including python-dotenv)
pip install .

## 3. Configuration
The project uses a `.env` file for configuration. If it doesn't exist, create it from the template:
```bash
cp .env.example .env
```
You can edit `.env` to change database credentials or ports.

## 4. Database Initialization
Run migrations and seed the database:
```bash
# Run migrations
alembic upgrade head

# Seed the database
python -m scripts.seed
```

## 4. Run the Application
Start the FastAPI server with hot-reload enabled:
```bash
uvicorn src.main:app --reload
```
The app will be available at [http://localhost:8000](http://localhost:8000).

---

### Database Connection
The application is configured to connect to `localhost:5432` by default when running natively. If you need to override the host, you can set the `DATABASE_HOST` environment variable:
```bash
DATABASE_HOST=127.0.0.1 uvicorn src.main:app --reload
```

### pgAdmin
You can access pgAdmin at [http://localhost:5050](http://localhost:5050) with:
- **Email**: `admin@admin.com`
- **Password**: `root`

### Troubleshooting
If you encounter `ImportError` regarding architecture (e.g., `mach-o file, but is an incompatible architecture`), you may need to recreate your virtual environment for your current architecture:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install .
```
