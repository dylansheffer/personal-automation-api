from pydantic import BaseModel, HttpUrl

class YouTubeURL(BaseModel):
    url: HttpUrl

class UserTakes(BaseModel):
    video_id: str
    takes: str