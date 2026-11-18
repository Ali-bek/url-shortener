# 🔗 URL Shortener with Analytics

A simple REST API that shortens URLs and tracks every click.
Built with **FastAPI**, **PostgreSQL** and **Docker**.

## Features
- Create short links (random or custom code)
- Full CRUD on links
- Click tracking (timestamp, referrer, user-agent)
- Analytics endpoint: total clicks, clicks per day, top referrers
- Auto-generated interactive docs (Swagger UI)
- Automated tests (pytest) and one-command Docker setup


## Try it
```bash
# Launch the API
http://localhost:8000

# See API Documentation
http://localhost:8000/docs

# Create a link
curl -X POST http://localhost:8000/api/links \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "custom_code": "gh"}'

# Visit it (tracked)
curl -i http://localhost:8000/gh

# See analytics
curl http://localhost:8000/api/links/gh/stats
```

## API overview
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/links` | Create a short link |
| GET | `/api/links` | List links |
| GET | `/api/links/{code}` | Get one link |
| PATCH | `/api/links/{code}` | Update target URL |
| DELETE | `/api/links/{code}` | Delete a link |
| GET | `/api/links/{code}/stats` | Click analytics |
| GET | `/{code}` | Redirect to the original URL |

## Architecture
```
Client ──► FastAPI routers ──► CRUD layer ──► SQLAlchemy ──► PostgreSQL
            (HTTP, validation)  (business logic)   (ORM)
                 ▲
            Pydantic schemas
```

| Layer | File | Responsibility |
|-------|------|----------------|
| Routers | `app/routers/` | Handle HTTP requests/responses, status codes |
| Schemas | `app/schemas.py` | Validate input and shape output (Pydantic) |
| CRUD | `app/crud.py` | All database queries and analytics aggregations |
| Models | `app/models.py` | Tables: `links` (1) ──< `clicks` (N) |
| Config/DB | `app/config.py`, `app/database.py` | Environment config, session management |

### Design decisions
- **307 redirect instead of 301**: permanent redirects are cached by browsers, which would bypass click tracking.
- **Random codes with `secrets`**: 62^7 combinations, with a collision check on creation.
- **Layered structure**: routes never touch the DB directly, which keeps the code testable.
- **Tests use in-memory SQLite** via FastAPI dependency overrides: fast, no external services needed.
- **Docker healthcheck**: the API only starts once PostgreSQL is ready.

## Running tests
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

## Possible improvements
- Alembic migrations instead of `create_all`
- Link expiration dates
- Rate limiting and API authentication
- Async click recording (background task / queue)
- Redis cache for hot links

## Tech stack
Python 3.13 · FastAPI · SQLAlchemy 2 · PostgreSQL 16 · Docker Compose · pytest