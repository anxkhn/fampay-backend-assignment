from fastapi import FastAPI
from routes import videos, ping
from utils.scheduler import start_scheduler
from database import create_db_and_tables

app = FastAPI()

app.include_router(videos.router)
app.include_router(ping.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    start_scheduler()
