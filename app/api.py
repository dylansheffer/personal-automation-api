from fastapi import APIRouter, HTTPException, BackgroundTasks
import openai
from dotenv import load_dotenv
import os
import asyncio
import json
import logging

from app.models import YouTubeURL, UserTakes
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
    generate_follow_up
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

def determine_transcription_errors(video_title, transcription):
    logger.info("Starting transcription error determination")
    system_prompt = TRANSCRIPTION_ERROR_SYSTEM_PROMPT

    user_prompt = f"""<|VIDEO_TITLE|>
{video_title}
<\|VIDEO_TITLE|>

<|TRANSCRIPT|>
{transcription}
</|TRANSCRIPT|>"""

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    logger.info("Sending request to OpenAI for transcription error determination")
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=conversation,
        response_format={"type": "json_object"}
    )

    result = json.loads(response['choices'][0]['message']['content'])
    logger.info(f"API Response: {json.dumps(result, indent=2)}")
    # Calculate cost for the first request
    total_cost = calculate_cost(response['usage'], model_costs, "gpt-4o-mini")
    
    # Filter out entries where confidence is False or final_answer.spelled_correct is True
    filtered_reasoning = []
    if 'reasoning' in result:
        logger.info(f"Number of reasoning entries before filtering: {len(result['reasoning'])}")
        for entry in result['reasoning']:
            logger.info(f"Processing entry: {json.dumps(entry, indent=2)}")
            spelled_correct = entry.get('final_answer', {}).get('spelled_correct', True)
            logger.info(f"Spelled Correct: {spelled_correct}")
            filtered_reasoning.append(entry)
    else:
        logger.warning("No 'reasoning' key found in the API response")

    logger.info(f"Number of filtered reasoning entries: {len(filtered_reasoning)}")
    
    if not filtered_reasoning:
        logger.info("No transcription errors found after filtering")
        return "No transcription errors found.", total_cost

    # Generate a markdown table of misspelled words
    system_prompt = """You are a helpful assistant. Your task is to create a markdown table of potentially misspelled words based on the user's supplied list, their context, and their likely correct spelling."""

    user_prompt = f"""Given the following list of potentially misspelled words and their context, create a markdown table with columns for 'Word', 'Context', and 'Likely Correct Spelling':

    {json.dumps(filtered_reasoning, indent=2)}

    Output the result as a markdown table. Do not surround in codeblocks"""

    logger.info(f"Sending request for markdown table generation with {len(filtered_reasoning)} entries")

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=conversation,
    )

    markdown_table = response['choices'][0]['message']['content']

    # Calculate cost for the second request and add it to the total
    total_cost += calculate_cost(response['usage'], model_costs, "gpt-4o-mini")

    logger.info(f"Markdown table generated: {markdown_table}")

    return markdown_table, total_cost

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

@router.get("/youtube_notes/transcription/{video_id}", tags=["Youtube notes"])
async def get_transcription_endpoint(video_id: str):
    transcription = get_transcription(video_id)
    return {"transcription": transcription}

@router.post("/youtube_notes/transcription_errors", tags=["Youtube notes"])
async def determine_transcription_errors_endpoint(video_id: str, video_title: str):
    transcription = get_transcription(video_id)
    errors, cost = determine_transcription_errors(video_title, transcription)
    return {"errors": errors, "cost": cost}

@router.post("/youtube_notes/generate_outline", tags=["Youtube notes"])
async def generate_outline_endpoint(video_id: str, model: str):
    video_details = get_video_details(video_id)
    transcription = get_transcription(video_id)
    errors, _ = determine_transcription_errors(video_details["title"], transcription)
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
    errors, _ = determine_transcription_errors(video_details["title"], transcription)
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
    errors, _ = determine_transcription_errors(video_details["title"], transcription)
    
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
    errors, error_cost = determine_transcription_errors(video_details["title"], transcription)
    
    outline, num_bullets, outline_cost = generate_outline(video_details["title"], video_details["channel"], transcription, errors, model)
    
    first_summary, first_cost = generate_summary(video_details["title"], video_details["channel"], transcription, errors, outline, 1, None, model)
    
    remaining_summaries = await generate_summaries_async(video_details["title"], video_details["channel"], transcription, errors, outline, num_bullets, first_summary, model)
    
    all_summaries = [first_summary] + [summary for summary, _ in remaining_summaries]
    summary_cost = first_cost + sum(cost for _, cost in remaining_summaries)
    
    combined_summaries = "\n\n".join(all_summaries)
    
    tldr, tldr_cost = generate_tldr(combined_summaries, model)
    vocabulary, vocab_cost = generate_vocabulary(transcription, errors, combined_summaries, model)
    
    summary_content = f"# {video_details['title']}\n\n"
    summary_content += f"<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{video_id}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>\n\n"
    summary_content += f"{tldr}\n\n## Key Vocabulary\n\n{vocabulary}\n\n{combined_summaries}"
    
    total_cost = error_cost + outline_cost + summary_cost + tldr_cost + vocab_cost
    
    title = video_details['title']
    file_name = f"{title.replace(':', '_')}.md"
    
    return {
        "video_id": video_id,
        "summary": summary_content,
        "transcription_errors": errors,
        "transcription": transcription,
        "cost": total_cost,
        "title": title,
        "file_name": file_name
    }