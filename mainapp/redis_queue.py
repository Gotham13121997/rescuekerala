import os

from rq import Queue

from redis_worker import conn

REDIS_URL = os.environ.get("REDIS_URL")

sms_queue = Queue(name="smsjob", connection=conn)
