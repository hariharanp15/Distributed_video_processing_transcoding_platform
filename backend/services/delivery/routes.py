import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Response
from services.common.config import MEDIA_ACCESS_TOKEN, MEDIA_ROOT
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.models import Video, VideoMetadata, ProcessingJob, ProcessingAttempt, TranscodingOutput, VideoThumbnail
from services.common.schemas import OutputOut, ThumbnailOut
router = APIRouter(tags=["delivery"])
def exists(video_id, db):
    if not db.get(Video, video_id): raise HTTPException(404, "Video not found")
def secure_url(url: str):
    return f"{url}?token={MEDIA_ACCESS_TOKEN}" if MEDIA_ACCESS_TOKEN else url
@router.get("/videos/{video_id}/outputs", response_model=list[OutputOut])
def outputs(video_id: str, db: Session = Depends(get_db)):
    exists(video_id, db); return [{"resolution": x.resolution, "url": secure_url(x.url), "status": x.status} for x in db.query(TranscodingOutput).filter_by(video_id=video_id)]
@router.get("/videos/{video_id}/thumbnails", response_model=list[ThumbnailOut])
def thumbnails(video_id: str, db: Session = Depends(get_db)):
    exists(video_id, db); return [{"url": secure_url(x.url), "status": x.status} for x in db.query(VideoThumbnail).filter_by(video_id=video_id)]

@router.delete("/videos/{video_id}", status_code=204)
def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Remove the upload, its service records, and its locally stored media."""
    video = db.get(Video, video_id)
    if not video: raise HTTPException(404, "Video not found")
    jobs = db.query(ProcessingJob).filter_by(video_id=video_id).all()
    job_ids = [job.id for job in jobs]
    if job_ids: db.query(ProcessingAttempt).filter(ProcessingAttempt.job_id.in_(job_ids)).delete(synchronize_session=False)
    db.query(TranscodingOutput).filter_by(video_id=video_id).delete(synchronize_session=False)
    db.query(VideoThumbnail).filter_by(video_id=video_id).delete(synchronize_session=False)
    db.query(ProcessingJob).filter_by(video_id=video_id).delete(synchronize_session=False)
    db.query(VideoMetadata).filter_by(video_id=video_id).delete(synchronize_session=False)
    db.delete(video); db.commit()
    root = Path(MEDIA_ROOT).resolve()
    upload = Path(video.storage_path).resolve()
    if upload.is_file() and root in upload.parents: upload.unlink()
    output_dir = (Path(MEDIA_ROOT) / "processed" / video_id).resolve()
    if output_dir.is_dir() and root in output_dir.parents: shutil.rmtree(output_dir)
    return Response(status_code=204)
