"""POST /tracks/get — authenticate user and return or trigger sync data."""

import httpx
import math
from fastapi import APIRouter, HTTPException, Request

from auth import verify_password
from config import WORKER_SECRET, WORKER_URL, TRACKS_ON_PAGE
from database import get_sync, get_album_info, get_track_by_slug, get_user, list_tracks, get_tracks_count
from models import TrackRequest, TrackResponse, TrackPreview, TrackRequestAll, ReturnTracks

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
        raise HTTPException(status_code=404, detail="Track not found")
    print(track['album_id'])
    album_data = await get_album_info(pool, track["album_id"])

    sync = await get_sync(pool, track["id"])
    if sync is not None:
        return TrackResponse(status="ok", data=sync["json_data"], album=album_data)

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{WORKER_URL}/process",
            json={"slug": body.slug},
            headers={"X-Worker-Secret": WORKER_SECRET},
        )

    return TrackResponse(status="processing", data=None)

@router.post("/list", response_model=ReturnTracks)
async def list_tracks_endpoint(
    body: TrackRequestAll,
    request: Request
):

    pool = request.app.state.pool

    user = await get_user(pool, body.username)

    if user is None or not verify_password(
        body.password,
        user["password_hash"]
    ):
        raise HTTPException(401, "Invalid credentials")

    tracks = await list_tracks(
        pool,
        body.page
    )

    total = await get_tracks_count(pool)

    return ReturnTracks(
        status="ok",
        page=body.page,
        total_pages=math.ceil(total / TRACKS_ON_PAGE),
        tracks=[
            TrackPreview(
                id=t["id"],
                title=t["title"],
                artists = t["artists"].split(", ") if t["artists"] else [],
                duration=t["duration"],
                album=t["album"],
                cover_url=t["cover_url"],
                likes=t["likes"],
                bpm=t["bpm"],
            )
            for t in tracks
        ]
    )