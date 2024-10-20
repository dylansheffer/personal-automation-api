from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
import openai
from dotenv import load_dotenv
import os
import asyncio
import json
import logging
import urllib.parse

from app.models import YouTubeURL, UserTakes, TranscriptionErrorResponse
from app.utils import (
    get_video_id,
    get_video_details,
    get_transcription,
    calculate_cost
)
from app.prompts import (
    TRANSCRIPTION_ERROR_SYSTEM_PROMPT,
    GENERATE_OUTLINE_SYSTEM_PROMPT,
    GENERATE_SUMMARY_SYSTEM_PROMPT,
    GENERATE_TLDR_SYSTEM_PROMPT,
    GENERATE_VOCABULARY_SYSTEM_PROMPT
)
from app.services import (
    generate_outline,
    generate_summary,
    generate_tldr,
    generate_vocabulary,
    generate_follow_up,
    determine_transcription_errors  # Ensure this import is present
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress debug messages
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Cost per 1,000 tokens for different models
model_costs = {
    "gpt-4o-mini": {
        "input": 0.000150,
        "output": 0.000600
    },
    "gpt-4o": {
        "input": 0.005,
        "output": 0.015
    },
}

router = APIRouter()

async def generate_summaries_async(video_title, video_author, transcription, transcription_errors, outline, num_bullets, first_summary, model):
    logger.info("Starting asynchronous summary generation")
    tasks = []
    for i in range(2, num_bullets + 1):
        tasks.append(asyncio.to_thread(generate_summary, video_title, video_author, transcription, transcription_errors, outline, i, first_summary, model))
    return await asyncio.gather(*tasks)

# YouTube Notes Endpoints

@router.post("/youtube_notes/video_details", tags=["Youtube notes"])
async def get_video_details_endpoint(youtube_url: YouTubeURL):
    video_id = get_video_id(str(youtube_url.url))
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    details = get_video_details(video_id)
    return {"video_id": video_id, "details": details}

@router.get("/youtube_notes/transcription", tags=["Youtube notes"])
async def get_transcription_endpoint(video_identifier: str = Query(..., description="YouTube URL or video ID")):
    # Decode the URL-encoded video_identifier
    video_identifier = urllib.parse.unquote(video_identifier)
    
    # Extract the video ID
    video_id = get_video_id(video_identifier)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL or ID")
    transcription = get_transcription(video_id)
    return {"transcription": transcription}

@router.post("/youtube_notes/transcription_errors", tags=["Youtube notes"])
async def determine_transcription_errors_endpoint(video_id: str, video_title: str, model: str):
    transcription = get_transcription(video_id)
    transcription_errors, cost = determine_transcription_errors(video_title, transcription, model)
    return {"errors": transcription_errors.errors, "cost": cost}

@router.post("/youtube_notes/generate_outline", tags=["Youtube notes"])
async def generate_outline_endpoint(video_id: str, model: str):
    video_details = get_video_details(video_id)
    transcription = get_transcription(video_id)
    errors, _ = determine_transcription_errors(video_details["title"], transcription, model)
    outline, num_bullets, cost = generate_outline(
        video_details["title"],
        video_details["channel"],
        transcription,
        errors,
        model
    )
    return {"outline": outline, "num_bullets": num_bullets, "cost": cost}

@router.post("/youtube_notes/generate_summary", tags=["Youtube notes"])
async def generate_summary_endpoint(video_id: str, model: str):
    video_details = get_video_details(video_id)
    transcription = get_transcription(video_id)
    errors, _ = determine_transcription_errors(video_details["title"], transcription, model)
    outline, num_bullets, _ = generate_outline(video_details["title"], video_details["channel"], transcription, errors, model)
    
    first_summary, first_cost = generate_summary(video_details["title"], video_details["channel"], transcription, errors, outline, 1, None, model)
    
    remaining_summaries = await generate_summaries_async(video_details["title"], video_details["channel"], transcription, errors, outline, num_bullets, first_summary, model)
    
    all_summaries = [first_summary] + [summary for summary, _ in remaining_summaries]
    total_cost = first_cost + sum(cost for _, cost in remaining_summaries)
    
    combined_summaries = "\n\n".join(all_summaries)
    
    tldr, tldr_cost = generate_tldr(combined_summaries, model)
    vocabulary, vocab_cost = generate_vocabulary(transcription, errors, combined_summaries, model)
    
    total_cost += tldr_cost + vocab_cost
    
    summary_content = f"# {video_details['title']}\n\n"
    summary_content += f"<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{video_id}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>\n\n"
    summary_content += f"{tldr}\n\n## Key Vocabulary\n\n{vocabulary}\n\n{combined_summaries}"
    
    return {"summary": summary_content, "cost": total_cost}

@router.post("/youtube_notes/generate_follow_up", tags=["Youtube notes"])
async def generate_follow_up_endpoint(user_takes: UserTakes, model: str):
    video_details = get_video_details(user_takes.video_id)
    transcription = get_transcription(user_takes.video_id)
    errors, _ = determine_transcription_errors(video_details["title"], transcription, model)
    
    follow_up_content, cost = generate_follow_up(video_details["title"], transcription, errors, user_takes.takes, model)
    
    title = f"RE: {video_details['title']}"
    file_name = f"RE_{video_details['title'].replace(':', '_')}.md"
    
    return {
        "follow_up": follow_up_content,
        "cost": cost,
        "title": title,
        "file_name": file_name
    }

@router.post("/youtube_notes/full_process", tags=["Youtube notes"])
async def full_process_endpoint(youtube_url: YouTubeURL, model: str, background_tasks: BackgroundTasks):
    video_id = get_video_id(str(youtube_url.url))
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    video_details = get_video_details(video_id)
    transcription = get_transcription(video_id)
    errors, error_cost = determine_transcription_errors(video_details["title"], transcription, model)
    
    # Add this line to convert errors to a dictionary
    errors_dict = errors.dict() if errors else {}
    
    outline, num_bullets, outline_cost = generate_outline(video_details["title"], video_details["channel"], transcription, errors_dict, model)
    
    first_summary, first_cost = generate_summary(video_details["title"], video_details["channel"], transcription, errors_dict, outline, 1, None, model)
    
    remaining_summaries = await generate_summaries_async(video_details["title"], video_details["channel"], transcription, errors_dict, outline, num_bullets, first_summary, model)
    
    all_summaries = [first_summary] + [summary for summary, _ in remaining_summaries]
    summary_cost = first_cost + sum(cost for _, cost in remaining_summaries)
    
    combined_summaries = "\n\n".join(all_summaries)
    
    tldr, tldr_cost = generate_tldr(combined_summaries, model)
    vocabulary, vocab_cost = generate_vocabulary(transcription, errors_dict, combined_summaries, model)
    
    summary_content = f"# {video_details['title']}\n\n"
    summary_content += f"<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{video_id}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>\n\n"
    summary_content += f"{tldr}\n\n## Key Vocabulary\n\n{vocabulary}\n\n{combined_summaries}"
    
    total_cost = error_cost + outline_cost + summary_cost + tldr_cost + vocab_cost
    
    title = video_details['title']
    file_name = f"{title.replace(':', '_')}.md"
    
    return {
        "video_id": video_id,
        "summary": summary_content,
        "transcription_errors": errors_dict,
        "transcription": transcription,
        "cost": total_cost,
        "title": title,
        "file_name": file_name
    }
