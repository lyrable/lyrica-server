TRACKLIST_QUERY = """SELECT
    t.id,
    t.title,
    t.duration,
    t.bpm,

    a.title AS album_title,
    a.cover_url,
    a.primary_color,

    COALESCE(s.likes, 0) AS likes,

    COALESCE(
        array_agg(ar.name) FILTER (WHERE ar.name IS NOT NULL),
        ARRAY[]::text[]
    ) AS artists

FROM tracks t

LEFT JOIN albums a
    ON a.id = t.album_id

LEFT JOIN track_artists ta
    ON ta.track_id = t.id

LEFT JOIN artists ar
    ON ar.id = ta.artist_id

LEFT JOIN LATERAL (
    SELECT likes
    FROM sync_versions
    WHERE track_id = t.id
    ORDER BY is_approved DESC, likes DESC
    LIMIT 1
) s ON TRUE

GROUP BY
    t.id,
    t.title,
    t.duration,
    t.bpm,
    t.album_id,
    a.title,
    a.cover_url,
    a.primary_color,
    s.likes

ORDER BY t.id DESC
LIMIT 30 OFFSET $1;"""