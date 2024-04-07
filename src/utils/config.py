from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
GOOGLE_API_KEYS = os.getenv("GOOGLE_API_KEYS").split(",")
QUERY = os.getenv("QUERY")
TIME_DELTA = int(os.getenv("TIME_DELTA"))
TIME_DELAY = int(os.getenv("TIME_DELAY"))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
INVIDIOUS_API = os.getenv("INVIDIOUS_API")
