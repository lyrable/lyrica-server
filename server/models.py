"""Pydantic request and response models for track and worker endpoints."""

from pydantic import BaseModel


class TrackRequest(BaseModel):
    username: str
    password: str
    slug: str
    artist: str | None
    title: str | None

class TrackRequestAll(BaseModel):
    username: str
    password: str
    page: int

class AccountCreate(BaseModel):
    username: str
    email: str | None = None
    password: str | None = None

class WorkerResult(BaseModel):
    slug: str
    json_data: dict


class TrackResponse(BaseModel):
    status: str  # "ok", "processing", "pending"
    data: dict | None = None
    album: dict | None = None

class TrackPreview(BaseModel):
    id: int
    title: str
    artists: list[str]
    duration: float | None
    bpm: float | None
    likes: int
    album: str | None
    cover_url: str | None
    primary_color: str | None


class ReturnTracks(BaseModel):
    status: str
    page: int
    total_pages: int
    tracks: list[TrackPreview]

class AccountResponse(BaseModel):
    status: str
    userid: int | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginFeedback(BaseModel):
    status: bool
    id: int | None = None

class TrackFile(BaseModel):
    id: int
    track_id: int
    storage_path: str
    file_size: int | None
    format: str
    bitrate: int | None
    sample_rate: int | None
    duration: float | None