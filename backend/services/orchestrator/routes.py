import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.models import Video, ProcessingJob
from services.common.schemas import ProcessRequest
from services.common.events import publish
from services.workers.processor import process as process_locally
from services.common.schemas import JobOut, ProcessOut
router = APIRouter(tags=["processing"])
@router.post("/videos/{video_id}/process", status_code=202, response_model=ProcessOut)
def process(video_id: str, request: ProcessRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    video = db.get(Video, video_id)
    if not video: raise HTTPException(404, "Video not found")
    active = db.query(ProcessingJob).filter(ProcessingJob.video_id == video_id, ProcessingJob.status.in_(["queued", "processing"])).first()
    if active:
        # Recover a process abandoned by an interrupted local worker or broker consumer.
        if active.status == "processing" and active.updated_at < datetime.utcnow() - timedelta(minutes=2):
            active.status = "queued"; video.status = "queued"; db.commit()
        if active.status == "queued": background_tasks.add_task(process_locally, json.dumps({"job_id": active.id, "video_id": video_id, "resolutions": request.resolutions}))
        return {"job_id": active.id, "status": active.status, "idempotent": True}
    # A retry reuses the most recent failed job. This prevents duplicate job
    # and output rows if users retry or RabbitMQ redelivers a message.
    previous = db.query(ProcessingJob).filter_by(video_id=video_id, status="failed").order_by(ProcessingJob.updated_at.desc()).first()
    if previous:
        previous.status = video.status = "queued"; previous.error_message = None; previous.progress = 0; db.commit()
        payload = {"job_id": previous.id, "video_id": video_id, "resolutions": request.resolutions}
        if not publish("video.process.requested", payload): background_tasks.add_task(process_locally, json.dumps(payload))
        return {"job_id": previous.id, "status": "queued", "retry": True}
    job = ProcessingJob(video_id=video_id); video.status = "queued"; db.add(job); db.commit()
    payload = {"job_id": job.id, "video_id": video_id, "resolutions": request.resolutions}
    if not publish("video.process.requested", payload): background_tasks.add_task(process_locally, json.dumps(payload))
    return {"job_id": job.id, "status": "queued"}
@router.get("/jobs/{job_id}", response_model=JobOut)
def job(job_id: str, db: Session = Depends(get_db)):
    result = db.get(ProcessingJob, job_id)
    if not result: raise HTTPException(404, "Job not found")
    return {"id": result.id, "video_id": result.video_id, "status": result.status, "progress": result.progress, "retries": result.retries, "error_message": result.error_message}
