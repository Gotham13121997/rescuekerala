import os

import redis
from rq import Worker, Queue, Connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'floodrelief.settings')

listen = ["high", "default", "low", "smsjob", "bulkcsvjob"]

redis_url = os.getenv("REDIS_URL")

conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
