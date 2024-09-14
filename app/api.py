from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import asyncio
import json
import logging
import time
import textwrap

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress debug messages from OpenAI library
logging.getLogger("openai").setLevel(logging.WARNING)
# Set up logging for urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
# Set up logging for asyncio
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Load environment variables from .env file
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

app = FastAPI()

class YouTubeURL(BaseModel):
    url: HttpUrl

class UserTakes(BaseModel):
    video_id: str
    takes: str

def get_video_id(url):
    logger.info(f"Attempting to extract video ID from URL: {url}")
    video_id = re.search(r'(?<=v=)[^&#]+', url)
    if not video_id:
        video_id = re.search(r'(?<=be/)[^&#]+', url)
    result = video_id.group(0) if video_id else None
    logger.info(f"Extracted video ID: {result}")
    return result

def get_video_details(video_id):
    logger.info(f"Fetching video details for video ID: {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "title": "Unknown Title",
            "channel": "Unknown Channel"
        }
        
        # Try to get title
        meta_title = soup.find('meta', {'name': 'title'})
        if meta_title and 'content' in meta_title.attrs:
            details["title"] = meta_title['content']
        else:
            title_tag = soup.find('title')
            if title_tag:
                details["title"] = title_tag.string.split(' - YouTube')[0]
        
        # Try to get channel name
        meta_channel = soup.find('meta', {'itemprop': 'channelName'})
        if meta_channel and 'content' in meta_channel.attrs:
            details["channel"] = meta_channel['content']
        else:
            channel_element = soup.select_one('a.yt-simple-endpoint.style-scope.yt-formatted-string')
            if channel_element:
                details["channel"] = channel_element.text.strip()
        
        logger.info(f"Retrieved video details: {details}")
        return details
    
    except requests.RequestException as e:
        logger.error(f"Error fetching video details: {str(e)}")
        return {
            "title": "Error Fetching Title",
            "channel": "Error Fetching Channel"
        }

def get_transcription(video_id):
    logger.info(f"Fetching transcription for video ID: {video_id}")
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            start_time = time.time()
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            end_time = time.time()

            transcription = " ".join([t['text'] for t in transcript])
            logger.info(f"Retrieved transcription (first 100 characters): {transcription[:100]}...")
            logger.info(f"Transcription fetch took {end_time - start_time:.2f} seconds")
            return transcription

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.error(f"No transcription available for video ID {video_id}: {str(e)}")
            return f"No transcription available: {str(e)}"

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Error fetching transcription (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to fetch transcription after {max_retries} attempts: {str(e)}")
                return f"Error fetching transcription: {str(e)}"

    return "Failed to fetch transcription after multiple attempts"

def calculate_cost(usage, model):
    input_cost = model_costs[model]["input"] * usage["prompt_tokens"] / 1000
    output_cost = model_costs[model]["output"] * usage["completion_tokens"] / 1000
    return input_cost + output_cost

def determine_transcription_errors(video_title, transcription):
    logger.info("Starting transcription error determination")
    system_prompt = """You are a master proof-reader who has a keen level of detail and uses context clues to identify new terms from misspelling. Your task is to be on the look out for transcription and spelling errors in a Youtube auto-generated video transcription. You accomplish this task by following this proven method:

1. Identify a list of words that are likely misspelled due to transcription errors. Use the specified transcription error criteria for finding the words to investigate.
2. Go word-by-word and reason whether the word in question is a spelling mistake. The reasoning follows a Socratic Method-like pattern of asking for a property and have you answer the question for a bit before reaching a final conclusion. 

Remember, it is ok to to initially consider a word as misspelled but determine that it is not misspelled. It is better to be safe rather than sorry! Making mistakes and realizing them is part of the process.  You must output in JSON following the specified structure. Only output in JSON without codeblocks.

<|TRANSCRIPTION_ERROR_CRITERIA|>
-  **Incorrect word recognition**: Automatic captions frequently misinterpret words, especially with accents or background noise.
-  **Complex vocabulary**: Technical terms or industry-specific jargon or brand new terms are commonly mistranscribed. Indicators of new words like proper nouns are often in the video title.
-  **Lack of punctuation**: Automatic captions often omit punctuation, making sentences harder to understand.
-  **Cultural biases**: Certain accents or dialects may be less accurately transcribed, reflecting biases in the underlying algorithms.
<\|TRANSCRIPTION_ERROR_CRITERIA|>
<|JSON_OUTPUT|>
# Output Shape

- to_investigate: str[] // List of words that meet transcription error criteria. Similar looking proper nouns could all be included
- list_of_similar_words: str[] // List of words that are in the transcript and are similar to the words to investigate. These may be indicators for the correct spelling
- reasoning: Reasoning[] // Your step-by-step reasoning for each word that follows the proven method

## Reasoning Shape
- term: str // the term that you are reasoning whether it is misspelled
- context: str // Provide the context in which the word appears, including if it is an acronym that is expanded later on
- reasoning: str // List your reasoning for why you believe it might be a spelling error. When thinking about unfamiliar proper nouns, compound words, or technical terms, think about the likely root words for the new word. It may inform the proper spelling
- final_answer: { scratch_pad: str, spelled_correct: bool, incorrect_spelling: str, correct_spelling: str } // Determine whether you think it is a spelling error. Use all the of your reasoning and the context of the video to make this determination. The incorrect spelling should be the exact string in question. The final correct spelling should also match the correct casing. For example llm would be LLM
- confident: bool // Whether you are 99 percent sure you are correct that your final answer is correct and is based on the context of the video
<\|JSON_OUTPUT|>
"""

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
    total_cost = calculate_cost(response['usage'], "gpt-4o-mini")
    
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
    total_cost += calculate_cost(response['usage'], "gpt-4o-mini")

    logger.info(f"Markdown table generated: {markdown_table}")

    return markdown_table, total_cost

def generate_outline(video_title, video_author, transcription, transcription_errors, model):
    logger.info("Starting outline generation")
    conversation_outline = [
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "system", "content": f"{transcription_errors}"},
        {"role": "user", "content": f"Your task is to first read the document titled '{video_title}' by {video_author} and output a detailed numbered outline of the document section by section. Provide high-level overviews of the subjects within each section. Output the result as a JSON object with two properties: 'outline' for the detailed outline in ol markdown list resembling a table of contents with detailed subchapters, and 'num_bullets' for the number of parent bullet points. Please make spelling corrections before writing the outline including correcting the spelling of the headings.\n\n{transcription}"}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation_outline,
        response_format={"type": "json_object"}
    )
    result = response['choices'][0]['message']['content']
    
    # Parse the JSON response
    parsed_result = json.loads(result)
    outline = parsed_result['outline']
    num_bullets = parsed_result['num_bullets']
    
    logger.info(f"Generated outline with {num_bullets} parent bullet points")
    return outline, num_bullets, calculate_cost(response['usage'], model)

def generate_summary(video_title, video_author, transcription, transcription_errors, outline, bullet_number, first_summary, model):
    logger.info(f"Starting summary generation for bullet {bullet_number}")
    conversation_summary = [
        {"role": "system", "content": "You are a helpful assistant designed to create structured summaries. You cover the essential information in your provided section and utilize complete sentences, lists, tables, quotes, etc to completely capture the original transcription."},
        {"role": "system", "content": f"{transcription_errors}"},
        {"role": "user", "content": f"Using this outline as a reference to ensure you're covering all the points mentioned in the outline for the video titled '{video_title}' by {video_author}, your task is to create a detailed summary that DOES NOT exclude important details and examples mentioned in the source text. Use the author's name instead of referring to them as the speaker. If you use their name instead of channel name, put the channel name in parentheses. You must output in a structured Markdown output with a proper heading structure starting at h2. You must include all the sub-bullets mentioned in the outline. Please make spelling corrections before writing the summary including correcting the spelling of the headings. Use all markdown features that are relevant to your summary such as tables, quotes, sub headings, etc. Be sure to correct spelling mistakes based on the identified problematic words above. Let's start with bullet {bullet_number}. **DO NOT** go beyond the bullet you are instructed to write. **DO NOT** output the number for the section title. **ONLY** output the summary for the bullet you are instructed to write. **DO NOT** output anything else. Summaries of a bullet do not need to end in a conclusion.\n---\n\n## Video Outline\n{outline}\n\n## Video Transcription\n{transcription}\n\n"}
    ]
    if first_summary and bullet_number > 1:
        conversation_summary.append({"role": "assistant", "content": first_summary})
        conversation_summary.append({"role": "user", "content": f"Now, please summarize bullet {bullet_number} in a similar style."})
    
    response = openai.ChatCompletion.create(model=model, messages=conversation_summary)
    summary = response['choices'][0]['message']['content']
    
    logger.info(f"Generated summary for bullet {bullet_number}")
    return summary, calculate_cost(response['usage'], model)

async def generate_summaries_async(video_title, video_author, transcription, transcription_errors, outline, num_bullets, first_summary, model):
    logger.info("Starting asynchronous summary generation")
    tasks = []
    for i in range(2, num_bullets + 1):
        tasks.append(asyncio.to_thread(generate_summary, video_title, video_author, transcription, transcription_errors, outline, i, first_summary, model))
    return await asyncio.gather(*tasks)

def generate_tldr(complete_summary, model):
    logger.info("Starting TL;DR generation")
    system_prompt = """You are a helpful assistant designed to create concise TL;DR (Too Long; Didn't Read) summaries. Your task is to create a brief, engaging summary that captures the main points of the given text in 2-3 sentences."""

    user_prompt = f"""Please create a TL;DR summary for the following text:

{complete_summary}

Your TL;DR should be 2-3 sentences long and capture the main points of the text."""

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation
    )

    tldr = response['choices'][0]['message']['content'].strip()
    cost = calculate_cost(response['usage'], model)

    logger.info(f"Generated TL;DR: {tldr}")
    logger.info(f"TL;DR generation cost: ${cost:.6f}")

    return tldr, cost

def generate_vocabulary(transcription, transcription_errors, combined_summaries, model):
    logger.info("Starting vocabulary generation")
    system_prompt = """You are a helpful assistant designed to extract key vocabulary from a given text. Your task is to identify and explain important terms, phrases, or concepts that are crucial to understanding the content."""

    user_prompt = f"""Please extract and explain key vocabulary from the following text. Focus on terms that are important for understanding the content, especially those that might be unfamiliar to a general audience.

Transcription:
{transcription}

Summary:
{combined_summaries}

Potential transcription errors:
{transcription_errors}

Please provide the vocabulary in a markdown format, with each term as a heading followed by its explanation."""

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation
    )

    vocabulary = response['choices'][0]['message']['content'].strip()
    cost = calculate_cost(response['usage'], model)

    logger.info(f"Generated vocabulary (first 100 characters): {vocabulary[:100]}...")
    logger.info(f"Vocabulary generation cost: ${cost:.6f}")

    return vocabulary, cost

@app.post("/video_details")
async def get_video_details_endpoint(youtube_url: YouTubeURL):
    video_id = get_video_id(str(youtube_url.url))
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    details = get_video_details(video_id)
    return {"video_id": video_id, "details": details}

@app.get("/transcription/{video_id}")
async def get_transcription_endpoint(video_id: str):
    transcription = get_transcription(video_id)
    return {"transcription": transcription}

@app.post("/transcription_errors")
async def determine_transcription_errors_endpoint(video_id: str, video_title: str):
    transcription = get_transcription(video_id)
    errors, cost = determine_transcription_errors(video_title, transcription)
    return {"errors": errors, "cost": cost}

@app.post("/generate_outline")
async def generate_outline_endpoint(video_id: str, model: str):
    video_details = get_video_details(video_id)
    transcription = get_transcription(video_id)
    errors, _ = determine_transcription_errors(video_details["title"], transcription)
    outline, num_bullets, cost = generate_outline(video_details["title"], video_details["channel"], transcription, errors, model)
    return {"outline": outline, "num_bullets": num_bullets, "cost": cost}

@app.post("/generate_summary")
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

@app.post("/generate_follow_up")
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

@app.post("/full_process")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)