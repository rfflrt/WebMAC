from fastapi import FastAPI
from redis import Redis
import os

app = FastAPI()

redis_host = os.getenv("REDIS_HOST", "localhost")
cache = Redis(host=redis_host, port=6379, decode_responses=True)

@app.get("/")
def index():
    hits = cache.incr("visitor_count")
    return {
        "message": "Olá visitante!",
        "total_visitors": hits
    }
