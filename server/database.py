"""asyncpg connection pool and raw SQL queries."""

import json

import asyncpg


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


async def get_user(pool: asyncpg.Pool, user_id: int) -> dict | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, password_hash FROM users WHERE id = $1",
            user_id,
        )
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
            "SELECT id, title, slug FROM tracks WHERE slug = $1",
            slug,
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
