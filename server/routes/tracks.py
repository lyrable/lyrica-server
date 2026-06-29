"""POST /tracks/get — authenticate user and return or trigger sync data."""

import httpx
import math
from fastapi import APIRouter, HTTPException, Request

from auth import verify_password
from config import WORKER_SECRET, WORKER_URL, TRACKS_ON_PAGE, AUDIO_DIR
from database import get_sync, get_album_info, get_track_by_slug, get_user, list_tracks, get_tracks_count, get_track_file
from models import TrackRequest, TrackResponse, TrackPreview, TrackRequestAll, ReturnTracks
import os
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/get", response_model=TrackResponse)
async def get_track(body: TrackRequest, request: Request) -> TrackResponse:
    pool = request.app.state.pool

    user = await get_user(pool, body.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    track = await get_track_by_slug(pool, body.slug)

    if track is None:
        if body.artist is None or body.title is None:
            raise HTTPException(status_code=404, detail="Track not found and artist/song name not provided")
        
        # Запустить обработку асинхронно
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{WORKER_URL}/process",
                json={"artist": body.artist, "title": body.title},
                headers={"X-Worker-Secret": WORKER_SECRET},
                timeout=5.0,
            )
        
        # Вернуть что трек на обработке
        return TrackResponse(
            status="processing",
            data=None,
            album=None,
        )

    # Если трек найден, продолжаем
    album_data = await get_album_info(pool, track["album_id"])
    sync = await get_sync(pool, track["id"])

    if sync is not None:
        return TrackResponse(status="ok", data=sync["json_data"], album=album_data)
    
    # Если синка нет
    return TrackResponse(status="pending", data=None, album=album_data)
    

@router.post("/list", response_model=ReturnTracks)
async def list_tracks_endpoint(body: TrackRequestAll, request: Request):
    pool = request.app.state.pool
    user = await get_user(pool, body.username)
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")

    tracks = await list_tracks(pool, body.page)
    total = await get_tracks_count(pool)

    return ReturnTracks(
        status="ok",
        page=body.page,
        total_pages=math.ceil(total / TRACKS_ON_PAGE),
        tracks=[
            TrackPreview(
                id=t["id"],
                title=t["title"],
                artists=t["artists"],
                duration=t["duration"],
                bpm=t["bpm"],
                likes=t["likes"],
                album=t["album_title"],
                cover_url=t["cover_url"],
                primary_color=t["primary_color"],
            )
            for t in tracks
        ]
    )

@router.get("/audio/{slug}")
async def get_audio(slug: str, request: Request):
    pool = request.app.state.pool

    track = await get_track_by_slug(pool, slug)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    track_file = await get_track_file(pool, track["id"])
    if track_file is None:
        raise HTTPException(status_code=404, detail="Audio not available")

    path = track_file["storage_path"]
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(path, media_type="audio/mpeg", filename=f"{slug}.mp3")