"""Load environment variables from .env for database and worker settings."""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
WORKER_SECRET = os.getenv("WORKER_SECRET", "").strip()
WORKER_URL = os.getenv("WORKER_URL", "").strip()
TRACKS_ON_PAGE = 30
