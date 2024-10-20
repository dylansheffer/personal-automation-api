import openai
import json
import logging
from app.utils import calculate_cost
from app.prompts import (
    GENERATE_OUTLINE_SYSTEM_PROMPT,
    GENERATE_SUMMARY_SYSTEM_PROMPT,
    GENERATE_TLDR_SYSTEM_PROMPT,
    GENERATE_VOCABULARY_SYSTEM_PROMPT,
    TRANSCRIPTION_ERROR_SYSTEM_PROMPT
)
from app.models import (
    TranscriptionErrorResponse,
    OutlineResponse,
    SummaryResponse,
    TranscriptionError
)
from app.config import model_costs

logger = logging.getLogger(__name__)

def generate_outline(video_title, video_author, transcription, transcription_errors, model):
    logger.info("Starting outline generation")
    conversation = [
        {"role": "system", "content": GENERATE_OUTLINE_SYSTEM_PROMPT.format(video_title=video_title, video_author=video_author)},
        {"role": "system", "content": json.dumps(transcription_errors, indent=2)},
        {"role": "user", "content": transcription}
    ]

    functions = [
        {
            "name": "outline_response",
            "description": "Generates an outline of the video content.",
            "parameters": OutlineResponse.schema()
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=conversation,
            functions=functions,
            function_call={"name": "outline_response"}
        )

        arguments = response['choices'][0]['message']['function_call']['arguments']
        outline_response = OutlineResponse.parse_raw(arguments)

        total_cost = calculate_cost(response['usage'], model_costs, model)

        return outline_response.outline, outline_response.num_bullets, total_cost
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        return None, 0, 0.0

def generate_summary(video_title, video_author, transcription, transcription_errors, outline, bullet_number, first_summary, model):
    logger.info(f"Starting summary generation for bullet {bullet_number}")
    conversation_summary = [
        {"role": "system", "content": GENERATE_SUMMARY_SYSTEM_PROMPT},
        {"role": "system", "content": json.dumps(transcription_errors, indent=2)},
        {"role": "user", "content": f"Using this outline as a reference to ensure you're covering all the points mentioned in the outline for the video titled '{video_title}' by {video_author}, your task is to create a detailed summary that DOES NOT exclude important details and examples mentioned in the source text. Let's start with bullet {bullet_number}.\n---\n\n## Video Outline\n{outline}\n\n## Video Transcription\n{transcription}\n\n"}
    ]
    if first_summary and bullet_number > 1:
        conversation_summary.append({"role": "assistant", "content": first_summary})
        conversation_summary.append({"role": "user", "content": f"Now, please summarize bullet {bullet_number} in a similar style."})
    
    response = openai.ChatCompletion.create(model=model, messages=conversation_summary)
    summary = response['choices'][0]['message']['content']
    
    logger.info(f"Generated summary for bullet {bullet_number}")
    return summary, calculate_cost(response['usage'], model_costs, model)

def generate_tldr(complete_summary, model):
    logger.info("Starting TL;DR generation")
    system_prompt = GENERATE_TLDR_SYSTEM_PROMPT

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
    cost = calculate_cost(response['usage'], model_costs, model)

    logger.info(f"Generated TL;DR (first 100 characters): {tldr[:100]}...")
    logger.info(f"TL;DR generation cost: ${cost:.6f}")

    return tldr, cost

def generate_vocabulary(transcription, transcription_errors, combined_summaries, model):
    logger.info("Starting vocabulary generation")
    system_prompt = GENERATE_VOCABULARY_SYSTEM_PROMPT

    user_prompt = f"""Please extract and explain key vocabulary from the following text. Focus on terms that are important for understanding the content, especially those that might be unfamiliar to a general audience.

Transcription:
{transcription}

Summary:
{combined_summaries}

Potential transcription errors:
{json.dumps(transcription_errors, indent=2)}

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
    cost = calculate_cost(response['usage'], model_costs, model)  # Add model_costs and model arguments
    
    logger.info(f"Generated vocabulary (first 100 characters): {vocabulary[:100]}...")
    logger.info(f"Vocabulary generation cost: ${cost:.6f}")

    return vocabulary, cost

def generate_follow_up(video_title, transcription, errors, user_takes, model):
    logger.info("Starting follow-up generation")
    prompt = f"""
    You are an AI assistant tasked with generating follow-up content based on a user's takes on a YouTube video.

    Video Title: {video_title}
    Transcription Errors: {', '.join(errors)}

    User's Takes:
    {' '.join(user_takes)}

    Based on the user's takes and the video content, generate a thoughtful follow-up that includes:
    1. A brief summary of the user's main points
    2. Additional insights or perspectives related to the user's takes
    3. Potential questions or areas for further exploration
    4. Any relevant connections to other topics or ideas

    Please format the follow-up content in Markdown.
    """

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    follow_up_content = response.choices[0].message['content'].strip()
    cost = calculate_cost(response['usage'], model)

    logger.info(f"Generated follow-up content")
    return follow_up_content, cost

def determine_transcription_errors(video_title, transcription, model):
    try:
        logger.info("Starting transcription error determination")
        system_prompt = TRANSCRIPTION_ERROR_SYSTEM_PROMPT

        user_prompt = f"""<|VIDEO_TITLE|>
{video_title}
</|VIDEO_TITLE|>

<|TRANSCRIPT|>
{transcription}
</|TRANSCRIPT|>"""

        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        functions = [
            {
                "name": "transcription_error_response",
                "description": "Parses transcription errors from the transcription.",
                "parameters": TranscriptionErrorResponse.schema()
            }
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=conversation,
            functions=functions,
            function_call={"name": "transcription_error_response"}
        )

        arguments = response['choices'][0]['message']['function_call']['arguments']
        transcription_errors = TranscriptionErrorResponse.parse_raw(arguments)

        total_cost = calculate_cost(response['usage'], model_costs, model)

        return transcription_errors, total_cost
    except Exception as e:
        logger.error(f"Error determining transcription errors: {e}")
        return None, 0.0
