from services.common.models import ProcessingJob
def test_job_creation_contract():
    job = ProcessingJob(video_id="video-1", status="queued", progress=0, retries=0)
    assert job.video_id == "video-1" and job.status == "queued" and job.progress == 0
