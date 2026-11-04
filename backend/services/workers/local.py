"""Run this only when using local mode without RabbitMQ.

It continuously claims queued jobs created by the API and processes them in
the same database. This is useful when the gateway is not kept open by an
interactive server background-task runner.
"""
import json
import time
from services.common.database import SessionLocal, Base, engine
from services.common.models import ProcessingJob
from services.workers.processor import process

Base.metadata.create_all(engine)
def main():
    print("Local video worker started. Press Ctrl+C to stop.")
    while True:
        db = SessionLocal()
        job = db.query(ProcessingJob).filter_by(status="queued").order_by(ProcessingJob.created_at).first()
        payload = {"job_id": job.id, "video_id": job.video_id} if job else None
        db.close()
        if payload: process(json.dumps(payload))
        else: time.sleep(2)
if __name__ == "__main__": main()
