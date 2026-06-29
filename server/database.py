"""asyncpg connection pool and raw SQL queries."""

import json

import asyncpg

from queries.tracklist import TRACKLIST_QUERY
from config import TRACKS_ON_PAGE


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def create_pool(database_url: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5,
        init=_init_connection,
    )
    
async def create_user(pool: asyncpg.Pool, email: str, username: str, password: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (id, email, username, password_hash)
            VALUES (nextval('users_id_seq'), $1, $2, $3)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            email, username, password,
        )
        return row['id'] if row else None

async def get_user(pool: asyncpg.Pool, username: str) -> dict | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, password_hash FROM users WHERE username = $1",
            username,
        )
        print(row)
        return dict(row) if row else None


async def get_sync(pool: asyncpg.Pool, track_id: int) -> dict | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT json_data FROM sync_versions
            WHERE track_id = $1
            ORDER BY is_approved DESC, likes DESC
            LIMIT 1
            """,
            track_id,
        )
        return dict(row) if row else None


async def get_track_by_slug(pool: asyncpg.Pool, slug: str) -> dict | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title, album_id, slug FROM tracks WHERE slug = $1",
            slug,
        )
        return dict(row) if row else None
    
async def list_tracks(pool: asyncpg.Pool, page: int):
    offset = (page - 1) * TRACKS_ON_PAGE
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            TRACKLIST_QUERY, offset)
    return [dict(r) for r in rows]
    
async def get_tracks_count(pool: asyncpg.Pool) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM tracks"
        )

async def get_album_info(pool: asyncpg.Pool, album_id: str) -> dict | None:
    if album_id is None:
        return None
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title, cover_url, release_date, likes, album_type, created_at FROM albums WHERE id = $1",
            album_id,
        )
        return dict(row) if row else None


async def save_sync(pool: asyncpg.Pool, track_id: int, json_data: dict) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO sync_versions (track_id, json_data)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            track_id,
            json_data,
        )

async def get_track_file(pool: asyncpg.Pool, track_id: int) -> dict | None:
    row = await pool.fetchrow(
        "SELECT * FROM track_files WHERE track_id = $1",
        track_id
    )
    return dict(row) if row else None

async def save_track_file(
    pool: asyncpg.Pool,
    track_id: int,
    storage_path: str,
    *,
    file_size: int | None = None,
    bitrate: int | None = None,
    sample_rate: int | None = None,
    duration: float | None = None,
) -> int:
    row = await pool.fetchrow(
        """
        INSERT INTO track_files
            (track_id, storage_path, file_size, format, bitrate, sample_rate, duration)
        VALUES ($1, $2, $3, 'mp3', $4, $5, $6)
        ON CONFLICT (track_id) DO UPDATE
            SET storage_path = EXCLUDED.storage_path,
                file_size    = COALESCE(EXCLUDED.file_size,    track_files.file_size),
                bitrate      = COALESCE(EXCLUDED.bitrate,      track_files.bitrate),
                sample_rate  = COALESCE(EXCLUDED.sample_rate,  track_files.sample_rate),
                duration     = COALESCE(EXCLUDED.duration,     track_files.duration),
                uploaded_at  = now()
        RETURNING id
        """,
        track_id, storage_path, file_size, bitrate, sample_rate, duration,
    )
    return row["id"]