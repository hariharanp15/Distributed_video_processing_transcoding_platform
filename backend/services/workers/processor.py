"""FFmpeg processing logic shared by RabbitMQ and local background workers."""
import json, shutil, subprocess
from pathlib import Path
from services.common.config import FFMPEG_BINARY, FFMPEG_PRESET, LOCAL_DEMO_FALLBACK, MEDIA_ROOT
from services.common.database import SessionLocal
from services.common.models import Video, ProcessingJob, ProcessingAttempt, TranscodingOutput, VideoThumbnail

def demo_outputs(video: Video, resolutions: list[str], output_dir: Path, db):
    """Local UI fallback. Copies source media and creates a labelled thumbnail.

    It is used only when FFmpeg is absent; production always follows FFmpeg.
    """
    for resolution in resolutions:
        target = output_dir / f"{resolution}.mp4"
        shutil.copy2(video.storage_path, target)
        output = db.query(TranscodingOutput).filter_by(video_id=video.id, resolution=resolution).first()
        if output: output.url = f"/media/processed/{video.id}/{resolution}.mp4"; output.status = "ready"
        else: db.add(TranscodingOutput(video_id=video.id, resolution=resolution, url=f"/media/processed/{video.id}/{resolution}.mp4"))
    thumbnail = output_dir / "thumbnail.svg"
    thumbnail.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360"><rect width="100%" height="100%" fill="#14233b"/><path d="M285 130l100 50-100 50z" fill="#3ac5a4"/><text x="32" y="325" fill="#e7edf7" font-family="Arial" font-size="24">{video.filename}</text></svg>', encoding="utf-8")
    existing = db.query(VideoThumbnail).filter_by(video_id=video.id).first()
    if existing: existing.url = f"/media/processed/{video.id}/thumbnail.svg"; existing.status = "ready"
    else: db.add(VideoThumbnail(video_id=video.id, url=f"/media/processed/{video.id}/thumbnail.svg"))

def process(body: str) -> bool:
    data = json.loads(body); db = SessionLocal(); job = db.get(ProcessingJob, data["job_id"]); video = db.get(Video, data["video_id"])
    if not job or job.status in ("completed", "processing"): db.close(); return True
    attempt = None
    try:
        # Attempt numbers are monotonic even after a worker interruption.
        previous = db.query(ProcessingAttempt).filter_by(job_id=job.id).order_by(ProcessingAttempt.attempt_number.desc()).first()
        attempt_number = (previous.attempt_number if previous else 0) + 1
        job.retries = attempt_number; job.status = video.status = "processing"
        attempt = ProcessingAttempt(job_id=job.id, attempt_number=attempt_number, status="processing")
        db.add(attempt); db.commit()
        binary = shutil.which(FFMPEG_BINARY) or (FFMPEG_BINARY if Path(FFMPEG_BINARY).is_file() else None)
        out_dir = Path(MEDIA_ROOT) / "processed" / video.id; out_dir.mkdir(parents=True, exist_ok=True)
        resolutions = data.get("resolutions", ["360p", "720p", "1080p"])
        if binary:
            for index, resolution in enumerate(resolutions, start=1):
                target = out_dir / f"{resolution}.mp4"
                subprocess.run([binary, "-y", "-i", video.storage_path, "-vf", f"scale=-2:{resolution[:-1]}", "-c:v", "libx264", "-preset", FFMPEG_PRESET, "-movflags", "+faststart", "-c:a", "aac", str(target)], check=True, capture_output=True, timeout=600)
                output = db.query(TranscodingOutput).filter_by(video_id=video.id, resolution=resolution).first()
                if output: output.url = f"/media/processed/{video.id}/{resolution}.mp4"; output.status = "ready"
                else: db.add(TranscodingOutput(video_id=video.id, resolution=resolution, url=f"/media/processed/{video.id}/{resolution}.mp4"))
                job.progress = int(index / len(resolutions) * 90); db.commit()
            thumb = out_dir / "thumbnail.jpg"; subprocess.run([binary, "-y", "-ss", "00:00:01", "-i", video.storage_path, "-frames:v", "1", str(thumb)], check=True, capture_output=True, timeout=120)
            thumbnail = db.query(VideoThumbnail).filter_by(video_id=video.id).first()
            if thumbnail: thumbnail.url = f"/media/processed/{video.id}/thumbnail.jpg"; thumbnail.status = "ready"
            else: db.add(VideoThumbnail(video_id=video.id, url=f"/media/processed/{video.id}/thumbnail.jpg"))
        elif LOCAL_DEMO_FALLBACK:
            demo_outputs(video, resolutions, out_dir, db)
        else:
            raise RuntimeError("FFmpeg is not installed or is not available on PATH. Install FFmpeg, set FFMPEG_BINARY if needed, then retry this job.")
        job.status = video.status = "completed"; job.progress = 100; db.commit(); return True
    except Exception as exc:
        db.rollback(); job = db.get(ProcessingJob, data["job_id"]); video = db.get(Video, data["video_id"])
        job.error_message = str(exc)[-1000:]; job.status = video.status = "failed"
        failed_attempt = db.query(ProcessingAttempt).filter_by(job_id=job.id, attempt_number=job.retries).first()
        if failed_attempt: failed_attempt.status = "failed"; failed_attempt.error_message = job.error_message
        db.commit(); return False
    finally: db.close()
