import json
from .config import RABBITMQ_URL
def publish(event: str, payload: dict):
    try:
        import pika
        conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)); ch = conn.channel(); ch.exchange_declare("video.events", "topic", durable=True)
        ch.basic_publish("video.events", event, json.dumps(payload), pika.BasicProperties(delivery_mode=2)); conn.close(); return True
    except Exception: return False  # Caller starts the local async fallback when no broker is available.
