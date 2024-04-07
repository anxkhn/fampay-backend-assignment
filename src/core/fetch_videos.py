from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils import config
from models import Video, FetchHistory
from datetime import datetime
from database import get_db
import redis
import requests

ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


def get_currenttime():
    return datetime.now().strftime(ISO_DATE_FORMAT)


def get_last_fetch_info():
    db = next(get_db())
    return db.query(FetchHistory).order_by(FetchHistory.last_fetch_time.desc()).first()


def update_fetch_history(last_video_id, last_fetch_time):
    db = next(get_db())
    fetch_history = FetchHistory(
        last_video_id=last_video_id,
        last_fetch_time=datetime.strptime(last_fetch_time, ISO_DATE_FORMAT),
    )
    db.add(fetch_history)
    db.commit()


def fetch_youtube_videos():
    last_successful_fetch = redis_client.get("last_successful_fetch")
    last_fetch_info = get_last_fetch_info()
    published_after_date = (
        datetime.strptime(last_successful_fetch.decode(), ISO_DATE_FORMAT)
        if last_successful_fetch
        else last_fetch_info.last_fetch_time
        if last_fetch_info
        else datetime(2024, 4, 7)
    )

    if (config.GOOGLE_API_KEYS)[0] == "":
        fetch_videos_from_invidious(published_after_date)
    else:
        fetch_videos_from_youtube(published_after_date)


def fetch_videos_from_youtube(published_after_date):
    db = next(get_db())
    keys_to_skip = {}
    key_index = 0
    last_video_id = None

    while True:
        key = config.GOOGLE_API_KEYS[key_index]
        if key in keys_to_skip:
            key_index = (key_index + 1) % len(config.GOOGLE_API_KEYS)
            continue

        try:
            youtube = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                developerKey=key,
            )
            search_response = (
                youtube.search()
                .list(
                    q=config.QUERY,
                    type="video",
                    part="snippet",
                    maxResults=50,
                    order="date",
                    publishedAfter=published_after_date.strftime(
                        ISO_DATE_FORMAT),
                )
                .execute()
            )
            last_video_id = process_youtube_response(search_response, db)
            print(f"Successful fetch from YouTube API: {key}")

            current_time = get_currenttime()
            redis_client.set("last_successful_fetch", current_time)
            update_fetch_history(last_video_id, current_time)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"An error occurred: {str(e)}")
            break

        except HttpError as e:
            print(f"Failed to fetch videos from YouTube API: {key}")
            if "quotaExceeded" in str(e):
                keys_to_skip[key] = True
                if len(keys_to_skip) == len(config.GOOGLE_API_KEYS):
                    print("All keys have exceeded quota.")
                    fetch_videos_from_invidious(published_after_date)
                    return
            else:
                print(f"Error details: {str(e)}")
                continue

        key_index = (key_index + 1) % len(config.GOOGLE_API_KEYS)


def process_youtube_response(response, db):
    last_video_id = None
    for search_result in response.get("items", []):
        video_data = Video(
            video_id=search_result["id"]["videoId"],
            title=search_result["snippet"]["title"],
            description=search_result["snippet"]["description"],
            published_at=datetime.strptime(
                search_result["snippet"]["publishedAt"], ISO_DATE_FORMAT
            ),
            thumbnails=str(search_result["snippet"]
                           ["thumbnails"]["high"]["url"]),
        )
        try:
            db.add(video_data)
            print(f"Video: {search_result['snippet']['title']}")
            last_video_id = video_data.video_id
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    return last_video_id


def fetch_videos_from_invidious(published_after_date):
    try:
        invidious_response = requests.get(
            config.INVIDIOUS_API,
            params={
                "q": config.QUERY,
                "sort_by": "upload_date",
                "duration": "short",
                "type": "videos",
            },
        )
        invidious_data = invidious_response.json()
        db = next(get_db())
        last_video_id = process_invidious_response(invidious_data, db)
        print("Successful fetch from invidious API")
        current_time = get_currenttime()
        update_fetch_history(last_video_id, current_time)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"An error occurred: {str(e)}")
    except Exception as e:
        print(f"Failed to fetch videos from invidious API: {str(e)}")


def process_invidious_response(response, db):
    last_video_id = None
    for item in response:
        published_at = datetime.utcfromtimestamp(item["published"]).strftime(
            ISO_DATE_FORMAT
        )

        published_at_datetime = datetime.strptime(
            published_at, ISO_DATE_FORMAT)

        maxres_thumbnail_url = None
        for thumbnail in item["videoThumbnails"]:
            if thumbnail["quality"] == "maxres":
                maxres_thumbnail_url = thumbnail["url"]
                break

        video_data = Video(
            video_id=item["videoId"],
            title=item["title"],
            description=item["description"],
            published_at=published_at_datetime,
            thumbnails=maxres_thumbnail_url,
        )
        try:
            db.add(video_data)
            print(f"Video: {item['title']}")
            last_video_id = video_data.video_id
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    return last_video_id
