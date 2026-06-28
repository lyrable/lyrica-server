TRACKLIST_QUERY = """SELECT
    t.id,
    t.title,
    t.duration,
    t.bpm,

    a.title AS album,
    a.cover_url,

    COALESCE(s.likes, 0) AS likes,

    string_agg(ar.name, ', ' ORDER BY ar.name) AS artists

FROM tracks t

LEFT JOIN album_tracks at
    ON at.track_id = t.id

LEFT JOIN albums a
    ON a.id = at.album_id

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
    a.title,
    a.cover_url,
    s.likes

ORDER BY t.id DESC

LIMIT 30
OFFSET $1;"""