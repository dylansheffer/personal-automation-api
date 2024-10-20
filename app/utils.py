import re
import logging
import requests
from bs4 import BeautifulSoup
import time
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound  # Add these imports
import urllib.parse  # Add this import
import os  # Add this import

logger = logging.getLogger(__name__)

# Set log level based on environment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

def get_video_id(identifier):
    logger.info(f"Attempting to extract video ID from identifier: {identifier}")
    
    # Decode the URL-encoded identifier
    identifier = urllib.parse.unquote(identifier)
    
    # Check if the identifier is already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', identifier):
        logger.info(f"Identifier is already a valid video ID: {identifier}")
        return identifier
    
    # Try to extract video ID from URL
    patterns = [
        r'(?<=v=)[^&#]+',       # Standard YouTube URL
        r'(?<=be/)[^&#]+',      # Shortened YouTube URL
        r'(?<=embed/)[^&#]+',   # Embedded YouTube URL
        r'(?<=youtu.be/)[^&#]+'  # youtu.be URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, identifier)
        if match:
            result = match.group(0)
            logger.info(f"Extracted video ID: {result}")
            return result
    
    logger.warning(f"Could not extract video ID from identifier: {identifier}")
    return None

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

        # Try multiple selectors for channel name
        selectors = [
            '#channel-name #text',
            'yt-formatted-string[id="text"][class="ytd-channel-name"]',
            'yt-formatted-string[class="ytd-channel-name"]',
            'a[class="yt-simple-endpoint style-scope yt-formatted-string"]'
        ]

        for selector in selectors:
            channel_element = soup.select_one(selector)
            if channel_element:
                details["channel"] = channel_element.text.strip()
                logger.info(f"Found channel name using selector: {selector}")
                break

        if details["channel"] == "Unknown Channel":
            logger.warning("Could not find channel name using any selector")
            logger.debug(f"HTML content length: {len(soup.prettify())}")
            with open('debug_html_content.log', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.debug("Full HTML content saved to debug_html_content.log")

        logger.info(f"Retrieved video details: {details}")
        return details

    except requests.RequestException as e:
        logger.error(f"Error fetching video details: {str(e)}")
        return {
            "title": "Error Fetching Title",
            "channel": "Error Fetching Channel"
        }

def get_transcription(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcription = " ".join([entry['text'] for entry in transcript_list])
        return transcription
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"No transcript available for video ID {video_id}: {e}")
        return ""

def calculate_cost(usage, model_costs, model):
    input_cost = usage.prompt_tokens * model_costs[model]["input"] / 1000
    output_cost = usage.completion_tokens * model_costs[model]["output"] / 1000
    return input_cost + output_cost
