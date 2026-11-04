from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.models import Video, VideoMetadata, ProcessingJob
from services.common.media_probe import probe_mp4
from services.common.schemas import MetadataOut, StatusOut, VideoDetailOut, VideoOut
router = APIRouter(tags=["metadata"])
@router.get("/videos", response_model=list[VideoOut])
def list_videos(db: Session = Depends(get_db)):
    return [{"id": v.id, "filename": v.filename, "status": v.status, "created_at": v.created_at} for v in db.query(Video).order_by(Video.created_at.desc()).all()]
@router.get("/videos/{video_id}", response_model=VideoDetailOut)
def video_details(video_id: str, db: Session = Depends(get_db)):
    video = db.get(Video, video_id); meta = db.get(VideoMetadata, video_id)
    if not video: raise HTTPException(404, "Video not found")
    # Hydrate files uploaded before the local MP4 probe was introduced.
    if meta and meta.format.lower() == "mp4" and (not meta.duration or not meta.width or not meta.height):
        try:
            duration, width, height = probe_mp4(video.storage_path)
            meta.duration = duration; meta.width = width; meta.height = height; db.commit()
        except (OSError, ValueError): pass
    return {"id": video.id, "filename": video.filename, "status": video.status, "created_at": video.created_at, "metadata": {"title": meta.title, "format": meta.format, "duration": meta.duration, "width": meta.width, "height": meta.height, "file_size": meta.file_size} if meta else None}
@router.get("/videos/{video_id}/metadata", response_model=MetadataOut)
def metadata(video_id: str, db: Session = Depends(get_db)):
    meta = db.get(VideoMetadata, video_id)
    if not meta: raise HTTPException(404, "Video metadata not found")
    return {"title": meta.title, "format": meta.format, "duration": meta.duration, "width": meta.width, "height": meta.height, "file_size": meta.file_size}
@router.get("/videos/{video_id}/status", response_model=StatusOut)
def status(video_id: str, db: Session = Depends(get_db)):
    video = db.get(Video, video_id)
    if not video: raise HTTPException(404, "Video not found")
    job = db.query(ProcessingJob).filter_by(video_id=video_id).order_by(ProcessingJob.created_at.desc()).first()
    return {"video_id": video_id, "status": video.status, "job": {"id": job.id, "video_id": job.video_id, "status": job.status, "progress": job.progress, "retries": job.retries, "error_message": job.error_message} if job else None}
