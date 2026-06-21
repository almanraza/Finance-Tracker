# Finance Manager — Backend API

FastAPI + PostgreSQL backend for the Personal Finance Manager iOS app.

## Stack
- **FastAPI** — async Python web framework
- **PostgreSQL** — primary database with proper indexes
- **SQLAlchemy** — ORM with connection pooling
- **Alembic** — database migrations
- **JWT** — access + refresh token auth
- **Claude AI** — automatic expense categorization
- **slowapi** — rate limiting
- **loguru** — structured logging
- **Sentry** — production error tracking

## Quick Start

### 1. Clone & setup env
```bash
cp .env.example .env
# Fill in your DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY
```

### 2. Run with Docker (recommended)
```bash
docker-compose up --build
```

### 3. Run locally
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/expenses/` | Create expense (AI categorizes) |
| GET | `/api/v1/expenses/` | List expenses (paginated + filtered) |
| GET | `/api/v1/expenses/summary` | Monthly summary by category |
| GET | `/api/v1/expenses/{id}` | Get single expense |
| PATCH | `/api/v1/expenses/{id}` | Update expense |
| DELETE | `/api/v1/expenses/{id}` | Delete expense |
| POST | `/api/v1/expenses/budgets/` | Set budget per category |
| GET | `/api/v1/expenses/budgets/` | Get budgets with spent amounts |

## Production Checklist
- [ ] Set `APP_ENV=production` in Railway env vars
- [ ] Set strong `SECRET_KEY` (32+ chars)
- [ ] Set `SENTRY_DSN` for error tracking
- [ ] Configure `CORS` origins to your actual domain
- [ ] Enable PostgreSQL backups on Railway
