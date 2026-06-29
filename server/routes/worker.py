"""POST /worker/result — worker callback to save processed sync data."""

from fastapi import APIRouter, Header, HTTPException, Request

from config import WORKER_SECRET
from database import get_track_by_slug, save_sync, save_track_file
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

import os, shutil
from fastapi import UploadFile, File, Form

AUDIO_DIR = os.getenv("AUDIO_DIR", "/data/audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

@router.post("/upload_audio")
async def upload_audio(
    request: Request,
    x_worker_secret: str = Header(),
    file: UploadFile = File(...),
    track_id: int = Form(...),
    bitrate: int | None = Form(None),
    sample_rate: int | None = Form(None),
    duration: float | None = Form(None),
):
    if x_worker_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    pool = request.app.state.pool

    dest = os.path.join(AUDIO_DIR, file.filename)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)

    file_size = os.path.getsize(dest)

    await save_track_file(
        pool, track_id, dest,
        file_size=file_size,
        bitrate=bitrate,
        sample_rate=sample_rate,
        duration=duration,
    )

    return {"status": "ok", "path": dest}