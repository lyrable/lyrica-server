"""FastAPI application entry point with lifespan pool management."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import DATABASE_URL
from database import create_pool
from routes import tracks, worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool(DATABASE_URL)
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
app.include_router(worker.router, prefix="/worker", tags=["worker"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
