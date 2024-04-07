from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Video

router = APIRouter()


@router.get("/videos")
def get_videos(db: Session = Depends(get_db), cursor: int = None, page_size: int = 10):
    query = db.query(Video).group_by(Video.video_id).order_by(Video.published_at.desc())

    if cursor:
        query = query.filter(Video.id < cursor)

    videos = query.limit(page_size).all()

    next_cursor = None
    if len(videos) == page_size:
        next_cursor = videos[-1].id

    return {"videos": videos, "next_cursor": next_cursor}
