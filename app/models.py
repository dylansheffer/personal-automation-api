from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class YouTubeURL(BaseModel):
    url: HttpUrl

class UserTakes(BaseModel):
    video_id: str
    takes: str

# New models for structured outputs
class TranscriptionError(BaseModel):
    word: str
    context: str
    likely_correct_spelling: str

class TranscriptionErrorResponse(BaseModel):
    errors: List[TranscriptionError]

class OutlineResponse(BaseModel):
    outline: str
    num_bullets: int

class SummaryResponse(BaseModel):
    summary: str
    cost: float