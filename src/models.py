from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    published_at = Column(DateTime)
    thumbnails = Column(String)


class FetchHistory(Base):
    __tablename__ = "fetch_history"

    id = Column(Integer, primary_key=True, index=True)
    last_video_id = Column(String)
    last_fetch_time = Column(DateTime)
