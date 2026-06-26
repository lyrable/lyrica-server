"""Pydantic request and response models for track and worker endpoints."""

from pydantic import BaseModel


class TrackRequest(BaseModel):
    user_id: int
    password: str
    slug: str


class WorkerResult(BaseModel):
    slug: str
    json_data: dict


class TrackResponse(BaseModel):
    status: str
    data: dict | None
