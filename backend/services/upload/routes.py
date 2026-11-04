from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from services.common.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, MEDIA_ROOT
from services.common.database import get_db
from services.common.models import Video, VideoMetadata
from services.common.events import publish
from services.common.media_probe import probe_mp4
from services.common.schemas import UploadOut

router = APIRouter(tags=["uploads"])
def validate_upload(name: str, size: int):
    if Path(name).suffix.lower() not in ALLOWED_EXTENSIONS: raise HTTPException(415, "Only mp4, mov, mkv, and webm are allowed")
    if size > MAX_UPLOAD_BYTES: raise HTTPException(413, "Video exceeds upload limit")
@router.post("/videos/upload", status_code=201, response_model=UploadOut)
async def upload_video(file: UploadFile = File(...), title: str = "", db: Session = Depends(get_db)):
    if not file.filename: raise HTTPException(422, "A filename is required")
    content = await file.read(); validate_upload(file.filename, len(content))
    video = Video(filename=file.filename, storage_path="pending"); db.add(video); db.flush()
    path = Path(MEDIA_ROOT) / "uploads" / f"{video.id}{Path(file.filename).suffix.lower()}"; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
    duration = width = height = 0
    if path.suffix.lower() == ".mp4":
        try: duration, width, height = probe_mp4(str(path))
        except (OSError, ValueError): pass
    video.storage_path = str(path); db.add(VideoMetadata(video_id=video.id, title=title or file.filename, format=path.suffix[1:], duration=duration, width=width, height=height, file_size=len(content))); db.commit()
    publish("video.uploaded", {"video_id": video.id}); return {"video_id": video.id, "status": video.status}
