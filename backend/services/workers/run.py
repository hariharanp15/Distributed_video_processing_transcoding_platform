"""RabbitMQ consumers. A job is idempotent: completed jobs are ACKed without rerunning FFmpeg."""
import json
import pika
from services.common.config import RABBITMQ_URL
from services.common.database import SessionLocal, Base, engine
from services.common.models import ProcessingJob
from services.workers.processor import process
Base.metadata.create_all(engine)
MAX_RETRIES = 3
def main():
    params = pika.URLParameters(RABBITMQ_URL); connection = pika.BlockingConnection(params); ch = connection.channel(); ch.exchange_declare("video.events", "topic", durable=True); ch.queue_declare("transcoding.dead", durable=True); ch.queue_declare("transcoding.jobs", durable=True); ch.queue_bind("transcoding.jobs", "video.events", "video.process.requested")
    def callback(channel, method, props, body):
        ok = process(body)
        if not ok:
            payload = json.loads(body); db = SessionLocal(); job = db.get(ProcessingJob, payload["job_id"]); retries = job.retries if job else MAX_RETRIES; db.close()
            destination = "video.process.requested" if retries < MAX_RETRIES else "video.process.dead"
            channel.basic_publish("video.events", destination, body, pika.BasicProperties(delivery_mode=2, headers={"x-retry-count": retries}))
            if retries >= MAX_RETRIES: channel.basic_publish("", "transcoding.dead", body, pika.BasicProperties(delivery_mode=2))
        channel.basic_ack(method.delivery_tag)
    ch.basic_qos(prefetch_count=1); ch.basic_consume("transcoding.jobs", callback); ch.start_consuming()
if __name__ == "__main__": main()
