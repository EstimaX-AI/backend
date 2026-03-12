import pika
import json
import os
import uuid
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

from db.database import SessionLocal
from db.models import ProcessingJob, JobStatus

load_dotenv(".env.dev")

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

_RETRY_DELAYS = [2, 4, 8, 16, 32]  # seconds


def _get_connection():
    credentials = pika.PlainCredentials(
        os.getenv("MQ_USER"),
        os.getenv("MQ_PASSWORD")
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv("MQ_HOST"),
        port=int(os.getenv("MQ_PORT")),
        virtual_host=os.getenv("MQ_VHOST"),
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(parameters)


def _save_result(job_id: str, status: str, result):
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.job_id == uuid.UUID(job_id)).first()
        if not job:
            raise ValueError(f"Job {job_id} not found in database")

        job.status = JobStatus.COMPLETED if status == "success" else JobStatus.FAILED
        job.result = result
        job.updated_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Job {job_id} saved with status={job.status}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save result for job {job_id}: {e}")
        raise
    finally:
        db.close()


def _on_message(channel, method, properties, body):
    try:
        payload = json.loads(body)
        logger.info(f"Received message: {payload}")

        job_id = payload["job_id"]
        status = payload["status"]
        result = payload["result"]

        # Validate UUID format before hitting the DB
        uuid.UUID(job_id)

        _save_result(job_id, status, result)

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Malformed message, discarding: {e} — body: {body}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Unexpected error processing message: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    attempt = 0
    while True:
        try:
            logger.info("Connecting to RabbitMQ...")
            connection = _get_connection()
            channel = connection.channel()

            channel.queue_declare(queue="result_queue", durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue="result_queue", on_message_callback=_on_message)

            attempt = 0  # reset backoff on successful connection
            logger.info("Listening on result_queue.")
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError,
                pika.exceptions.ConnectionClosedByBroker,
                pika.exceptions.StreamLostError) as e:
            delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
            logger.error(f"RabbitMQ connection lost: {e}. Reconnecting in {delay}s...")
            time.sleep(delay)
            attempt += 1

        except Exception as e:
            logger.error(f"Consumer crashed unexpectedly: {e}. Retrying in 5s...")
            time.sleep(5)
