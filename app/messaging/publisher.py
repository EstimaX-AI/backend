import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()

def publish_to_queue(queue_name, message):

    credentials = pika.PlainCredentials(
        os.getenv("MQ_USER"),
        os.getenv("MQ_PASSWORD")
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("MQ_HOST"),
        port=int(os.getenv("MQ_PORT")),
        virtual_host=os.getenv("MQ_VHOST"),
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()