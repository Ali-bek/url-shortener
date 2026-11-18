from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import links, redirect


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # creates tables at startup
    yield


app = FastAPI(
    title="URL Shortener with Analytics",
    description="Shorten URLs and track clicks. Built with FastAPI, PostgreSQL and Docker.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(links.router)

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(redirect.router)  # included last: /{code} is a catch-all
