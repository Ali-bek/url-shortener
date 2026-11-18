import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/shortener"
)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")