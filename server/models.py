"""Pydantic request and response models for track and worker endpoints."""

from pydantic import BaseModel


class TrackRequest(BaseModel):
    username: str
    password: str
    slug: str

class TrackRequestAll(BaseModel):
    username: str
    password: str

class AccountCreate(BaseModel):
    username: str
    email: str | None = None
    password: str | None = None

class WorkerResult(BaseModel):
    slug: str
    json_data: dict


class TrackResponse(BaseModel):
    status: str
    data: dict | None
    album: dict | None

class ReturnTracks(BaseModel):
    status: str
    data: dict | None = None

class AccountResponse(BaseModel):
    status: str
    userid: int | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginFeedback(BaseModel):
    status: bool
    id: int | None = None