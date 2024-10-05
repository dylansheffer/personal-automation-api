import re
import logging
import requests
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

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
                logger.warning(
                    f"Error fetching transcription (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to fetch transcription after {max_retries} attempts: {str(e)}")
                return f"Error fetching transcription: {str(e)}"

    return "Failed to fetch transcription after multiple attempts"

def calculate_cost(usage, model_costs, model):
    input_cost = model_costs[model]["input"] * usage["prompt_tokens"] / 1000
    output_cost = model_costs[model]["output"] * usage["completion_tokens"] / 1000
    return input_cost + output_cost