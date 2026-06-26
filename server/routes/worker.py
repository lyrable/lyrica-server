"""POST /worker/result — worker callback to save processed sync data."""

from fastapi import APIRouter, Header, HTTPException, Request

from config import WORKER_SECRET
from database import get_track_by_slug, save_sync
from models import WorkerResult

router = APIRouter()


@router.post("/result")
async def worker_result(
    body: WorkerResult,
    request: Request,
    x_worker_secret: str = Header(),
) -> dict:
    if x_worker_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    pool = request.app.state.pool

    track = await get_track_by_slug(pool, body.slug)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    await save_sync(pool, track["id"], body.json_data)
    return {"status": "saved"}
