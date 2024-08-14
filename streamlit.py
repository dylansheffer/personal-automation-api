import streamlit as st
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
import textwrap
import time

# TODO make it possible to stop between each step and adjust the value before continuing. I would also like toggles whether I'd like it to stop at a particular step or just continue automatically. Maybe a complete auto at the top and then sub toggles under. I would like an edit button that let's me tweak the generated content before it continues on.
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
            channel_element = soup.select_one('yt-formatted-string#text.ytd-channel-name')
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
    retry_delay = 5  # seconds

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
    input_tokens = usage['prompt_tokens']
    output_tokens = usage['completion_tokens']
    input_cost = (input_tokens / 1000) * model_costs[model]['input']
    output_cost = (output_tokens / 1000) * model_costs[model]['output']
    total_cost = input_cost + output_cost
    logger.info(f"Calculated cost for model {model}: ${total_cost:.6f}")
    return total_cost

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
            # if not spelled_correct:
            #     filtered_reasoning.append(entry)
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
    conversation_tldr = [
        {"role": "system", "content": "You are a helpful assistant designed to create concise and punchy summaries."},
        {"role": "user", "content": f"Create a TL;DR of the provided text. Use H2 for the TL;DR heading.\n\n---\n\n{complete_summary}. **ONLY** output the TL;DR you are instructed to write. **DO NOT** output anything else."}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_tldr)
    tldr = response['choices'][0]['message']['content']
    
    cost = calculate_cost(response['usage'], model)
    
    conversation_tldr += [{"role": "assistant", "content": tldr},
                          {"role": "user", "content": "Now, make this TL;DR even punchier and more concise."}]
    response_punchy = openai.ChatCompletion.create(model=model, messages=conversation_tldr)
    
    cost += calculate_cost(response_punchy['usage'], model)
    
    logger.info("Completed TL;DR generation")
    return response_punchy['choices'][0]['message']['content'], cost

def generate_vocabulary(transcription, transcription_errors, generated_notes, model):
    logger.info("Starting vocabulary generation")
    conversation_vocab = [
        {"role": "system", "content": "You are a helpful assistant designed to extract and define key vocabulary terms."},
        {"role": "system", "content": f"{transcription_errors}"},
        {"role": "user", "content": f"Extract important vocabulary words from the following transcription and generated notes, considering the potential transcription errors mentioned above. For each term, provide a concise definition. Format the output in markdown, with each term-definition pair in the format '> **Key Term**: {{definition}}'. Limit the output to 10 key terms. Focus on terms that are central to the video's content or are important for understanding the video's meaning. Please make spelling corrections before writing terms. Only output the markdown text without codeblocks. \n\n---\n\n## Transcription\n{transcription}\n\n## Generated Notes\n{generated_notes}"}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_vocab)
    vocabulary = response['choices'][0]['message']['content']
    
    cost = calculate_cost(response['usage'], model)
    
    return vocabulary, cost

def generate_follow_up(video_title, transcription, transcription_errors, user_takes, model):
    system_prompt = """You are an AI assistant tasked with analyzing a video transcription and user's takes on the video. 
    Generate a follow-up document with the following sections:
    1. TL;DR: A brief summary of the main points.
    2. Resonance: Ideas that resonated with the user from the video.
    3. Dissonance: Disagreements or conflicts in ideas.
    4. Harmony: Ideas that are separate but related.
    5. Modulation: New ideas derived from the video.
    
    Use the transcription, identified transcription errors, and user's takes to inform your analysis.
    Format your response in markdown, using h2 headings for each section."""

    user_prompt = f"""Video Title: {video_title}

Transcription:
{transcription}

Transcription Errors:
{transcription_errors}

User's Takes:
{user_takes}

Please generate the follow-up document as described."""

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation
    )

    follow_up_content = response['choices'][0]['message']['content']
    cost = calculate_cost(response['usage'], model)

    return follow_up_content, cost

def main():
    st.title("YouTube Video Summarizer")

    # Initialize session state variables
    if 'youtube_url' not in st.session_state:
        st.session_state.youtube_url = ''
    if 'summary_generated' not in st.session_state:
        st.session_state.summary_generated = False
    if 'follow_up_generated' not in st.session_state:
        st.session_state.follow_up_generated = False
    if 'total_cost' not in st.session_state:
        st.session_state.total_cost = 0.0
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ''
    if 'transcription_errors' not in st.session_state:
        st.session_state.transcription_errors = ''
    if 'video_title' not in st.session_state:
        st.session_state.video_title = ''
    if 'summary_content' not in st.session_state:
        st.session_state.summary_content = ''
    if 'follow_up_content' not in st.session_state:
        st.session_state.follow_up_content = ''

    model = st.selectbox("Choose the model", ["gpt-4o-mini","gpt-4o"])

    youtube_url = st.text_input("Enter YouTube URL", value=st.session_state.youtube_url)

    if youtube_url:
        st.session_state.youtube_url = youtube_url
        video_id = get_video_id(youtube_url)
        if video_id:
            st.video(youtube_url)

            # Create tabs
            summary_tab, follow_up_tab = st.tabs(["Summary", "Follow-up"])

            with summary_tab:
                if st.button("Generate Summary") or st.session_state.summary_generated:
                    if not st.session_state.summary_generated:
                        st.session_state.summary_generated = True
                        st.session_state.total_cost = 0.0

                        with st.spinner("Generating summary..."):
                            start_time = time.time()

                            # Fetch video details
                            st.spinner("Fetching video details")
                            video_details = get_video_details(video_id)
                            st.session_state.video_title = video_details["title"]
                            video_author = video_details["channel"]
                            logger.info(f"Video details fetched in {time.time() - start_time:.2f} seconds")

                            # Fetch transcription
                            transcription_start = time.time()
                            st.spinner("Fetching video transcription")
                            st.session_state.transcription = get_transcription(video_id)
                            logger.info(f"Transcription fetched in {time.time() - transcription_start:.2f} seconds")

                            # Display the transcription in a collapsible section
                            with st.expander("View Transcription"):
                                st.text_area("Video Transcription", value=st.session_state.transcription, height=300, disabled=True)

                            # Determine transcription errors
                            st.spinner("Determining transcription errors...")
                            st.session_state.transcription_errors, error_cost = determine_transcription_errors(st.session_state.video_title, st.session_state.transcription)
                            st.session_state.total_cost += error_cost

                            # Generate outline
                            st.spinner("Generating outline...")
                            outline, num_bullets, outline_cost = generate_outline(st.session_state.video_title, video_author, st.session_state.transcription, st.session_state.transcription_errors, model)
                            st.session_state.total_cost += outline_cost

                            # Generate summary for bullet 1
                            st.spinner("Generating summary for first bullet point...")
                            first_summary, first_summary_cost = generate_summary(st.session_state.video_title, video_author, st.session_state.transcription, st.session_state.transcription_errors, outline, 1, None, model)
                            st.session_state.total_cost += first_summary_cost

                            # Generate summaries for remaining bullets
                            st.spinner("Generating summaries for remaining bullet points...")
                            bullet_summaries = [first_summary]
                            remaining_summaries = asyncio.run(generate_summaries_async(st.session_state.video_title, video_author, st.session_state.transcription, st.session_state.transcription_errors, outline, num_bullets, first_summary, model))
                            for i, (summary, cost) in enumerate(remaining_summaries, start=2):
                                bullet_summaries.append(summary)
                                st.session_state.total_cost += cost

                            combined_summaries = "\n\n".join(bullet_summaries)

                            # Generate TL;DR
                            st.spinner("Generating TL;DR...")
                            tldr, tldr_cost = generate_tldr(combined_summaries, model)
                            st.session_state.total_cost += tldr_cost

                            # Generate vocabulary
                            st.spinner("Generating key vocabulary...")
                            vocabulary, vocab_cost = generate_vocabulary(st.session_state.transcription, st.session_state.transcription_errors, combined_summaries, model)
                            st.session_state.total_cost += vocab_cost

                            # Generate summary content
                            st.spinner("Compiling final summary...")
                            st.session_state.summary_content = f"# {st.session_state.video_title}\n\n"
                            st.session_state.summary_content += f"<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{video_id}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>\n\n"
                            st.session_state.summary_content += f"{tldr}\n\n## Key Vocabulary\n\n{vocabulary}\n\n{combined_summaries}"

                            logger.info(f"Total summary generation time: {time.time() - start_time:.2f} seconds")

                    # Display the summary and other generated content
                    st.markdown("## Summary")
                    st.markdown(st.session_state.summary_content)
                    st.markdown("## Potential Transcription Errors")
                    st.markdown(st.session_state.transcription_errors)

            with follow_up_tab:
                user_takes = st.text_area("Enter your takes on the video (as an unordered list in markdown):")

                if st.button("Generate Follow-up") or st.session_state.follow_up_generated:
                    if not st.session_state.follow_up_generated:
                        st.session_state.follow_up_generated = True
                        with st.spinner("Generating follow-up document..."):
                            st.session_state.follow_up_content, follow_up_cost = generate_follow_up(
                                st.session_state.video_title, 
                                st.session_state.transcription, 
                                st.session_state.transcription_errors, 
                                user_takes, 
                                model
                            )
                            st.session_state.total_cost += follow_up_cost

                    st.markdown("## Follow-up Document")
                    st.markdown(st.session_state.follow_up_content)

                    follow_up_file_name = f"RE - {st.session_state.video_title}.md"
                    with open(follow_up_file_name, "w") as file:
                        file.write(st.session_state.follow_up_content)

                    with open(follow_up_file_name, "rb") as file:
                        st.download_button(
                            label="Download Follow-up Document",
                            data=file,
                            file_name=follow_up_file_name,
                            mime="text/markdown"
                        )

            st.markdown(f"# Total Cost: ${st.session_state.total_cost:.2f}")

            if st.button("Reset"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()

        else:
            st.error("Invalid YouTube URL")

if __name__ == "__main__":
    main()