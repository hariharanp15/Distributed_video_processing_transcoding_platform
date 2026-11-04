import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./video_platform.db")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "media")
MEDIA_ACCESS_TOKEN = os.getenv("MEDIA_ACCESS_TOKEN", "")
FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg")
FFMPEG_PRESET = os.getenv("FFMPEG_PRESET", "medium")
# Development-only fallback keeps the complete local workflow demonstrable
# on machines where FFmpeg has not yet been installed.
LOCAL_DEMO_FALLBACK = os.getenv("LOCAL_DEMO_FALLBACK", "true").lower() == "true"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(500 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
