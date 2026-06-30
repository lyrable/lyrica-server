# Lyrica Server — `api.lyricapp.ru / db.lyricapp.ru`

Серверная часть Lyrica

Аутентификация — по паре `username/password` в теле каждого запроса (без токенов/сессий), пароли хешируются через `passlib/bcrypt`.

## Стек

- FastAPI, asyncpg, httpx, passlib/bcrypt
- nginx + Certbot (HTTPS), systemd (`lyrica.service`)
- PostgreSQL (домен `db.lyricapp.ru`)

## Эндпоинты

### `/accounts`

| Метод | Путь | Тело | Описание |
|---|---|---|---|
| POST | `/accounts/create` | `AccountCreate {email, username, password}` | Регистрация. 401 — если юзернейм занят или пароль не передан |
| POST | `/accounts/login` | `LoginRequest {username, password}` | Логин. 400 — пустые поля, 401 — неверные данные |

### `/tracks`

| Метод | Путь | Тело | Описание |
|---|---|---|---|
| POST | `/tracks/get` | `TrackRequest {username, password, slug, artist?, title?}` | Возвращает синк трека. Нет трека в БД → асинхронный вызов `worker/process`, ответ `status="processing"`. Трек есть, синка нет → `status="pending"`. Есть синк → `status="ok"` + данные синка и альбома |
| POST | `/tracks/list` | `TrackRequestAll {username, password, page}` | Пагинированный список треков (размер страницы — `TRACKS_ON_PAGE` из конфига) |
| GET | `/tracks/audio/{slug}` | — | Отдаёт MP3-файл трека (`FileResponse`). 404 — трек/файл не найден |

### `/worker` (защищено заголовком `X-Worker-Secret`)

| Метод | Путь | Тело | Описание |
|---|---|---|---|
| POST | `/worker/result` | `WorkerResult {slug, json_data}` + header `X-Worker-Secret` | Воркер пишет готовый синк (тайминги) в БД |
| POST | `/worker/upload_audio` | multipart: `file`, `track_id`, `bitrate?`, `sample_rate?`, `duration?` + header `X-Worker-Secret` | Воркер заливает обработанный аудиофайл, путь и метаданные сохраняются в БД |

## Архитектура БД
<img width="1216" height="842" alt="5336825447918017879" src="https://github.com/user-attachments/assets/65a33f7c-8e25-45f4-a9e5-89eb64d911d8" />

## Установка ПО на сервер

Текущий набор эндпоинтов **требует** FastAPI, asyncpg, httpx, passlib.
