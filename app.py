import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import asyncio
import json
import logging
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
    video_id = re.search(r'(?<=v=)[^&#]+', url)
    if not video_id:
        video_id = re.search(r'(?<=be/)[^&#]+', url)
    return video_id.group(0) if video_id else None

def get_video_title(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('meta', {'name': 'title'})['content']
    return title

def get_video_author(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author_element = soup.select_one('div#container.style-scope.ytd-channel-name a.yt-simple-endpoint')
    return author_element.text if author_element else "Unknown Author"

def get_transcription(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t['text'] for t in transcript])

def calculate_cost(usage, model):
    input_tokens = usage['prompt_tokens']
    output_tokens = usage['completion_tokens']
    input_cost = (input_tokens / 1000) * model_costs[model]['input']
    output_cost = (output_tokens / 1000) * model_costs[model]['output']
    return input_cost + output_cost

def determine_transcription_errors(video_title, transcription):
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
    
    return outline, num_bullets, calculate_cost(response['usage'], model)

def generate_summary(video_title, video_author, transcription, transcription_errors, outline, bullet_number, first_summary, model):
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
    
    return summary, calculate_cost(response['usage'], model)

async def generate_summaries_async(video_title, video_author, transcription, transcription_errors, outline, num_bullets, first_summary, model):
    tasks = []
    for i in range(2, num_bullets + 1):
        tasks.append(asyncio.to_thread(generate_summary, video_title, video_author, transcription, transcription_errors, outline, i, first_summary, model))
    return await asyncio.gather(*tasks)

def generate_tldr(complete_summary, model):
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
    
    return response_punchy['choices'][0]['message']['content'], cost

def generate_vocabulary(transcription, transcription_errors, generated_notes, model):
    conversation_vocab = [
        {"role": "system", "content": "You are a helpful assistant designed to extract and define key vocabulary terms."},
        {"role": "system", "content": f"{transcription_errors}"},
        {"role": "user", "content": f"Extract important vocabulary words from the following transcription and generated notes, considering the potential transcription errors mentioned above. For each term, provide a concise definition. Format the output in markdown, with each term-definition pair in the format '> **Key Term**: {{definition}}'. Limit the output to 10 key terms. Focus on terms that are central to the video's content or are important for understanding the video's meaning. Please make spelling corrections before writing terms. Only output the markdown text without codeblocks. \n\n---\n\n## Transcription\n{transcription}\n\n## Generated Notes\n{generated_notes}"}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_vocab)
    vocabulary = response['choices'][0]['message']['content']
    
    cost = calculate_cost(response['usage'], model)
    
    return vocabulary, cost

def main():
    st.title("YouTube Video Summarizer")

    model = st.selectbox("Choose the model", ["gpt-4o-mini","gpt-4o"])

    youtube_url = st.text_input("Enter YouTube URL")

    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            st.video(youtube_url)

            if st.button("Summarize"):
                total_cost = 0.0

                with st.spinner("Fetching video title..."):
                    video_title = get_video_title(video_id)

                with st.spinner("Fetching video author..."):
                    video_author = get_video_author(video_id)

                with st.spinner("Fetching transcription..."):
                    transcription = get_transcription(video_id)
                    # Save the transcription to a file
                    with open(f"{video_title}_transcription.txt", "w", encoding="utf-8") as file:
                        file.write(transcription)

                with st.spinner("Determining transcription errors..."):
                    transcription_errors, error_cost = determine_transcription_errors(video_title, transcription)
                    total_cost += error_cost
                    st.markdown("## Potential Transcription Errors")
                    st.markdown(transcription_errors)

                with st.spinner("Generating outline..."):
                    outline, num_bullets, outline_cost = generate_outline(video_title, video_author, transcription, transcription_errors, model)
                    total_cost += outline_cost
                
                    outline_markdown = "# Outline\n\n"
                    for item in outline:
                        if isinstance(item, dict):
                            # Assuming the dict has 'number' and 'text' keys
                            number = item.get('number', '')
                            text = item.get('text', '')
                            if '.' in number:
                                # This is a sub-bullet
                                outline_markdown += f"    {text}\n"
                            else:
                                # This is a parent bullet
                                outline_markdown += f"{text}\n"
                        elif isinstance(item, str):
                            # If it's a string, just add it as is
                            outline_markdown += f"{item}\n"
                        else:
                            # For any other unexpected type, convert to string and add
                            outline_markdown += f"{str(item)}\n"
                    
                    st.markdown(outline_markdown)

                with st.spinner("Generating summary for bullet 1..."):
                    first_summary, first_summary_cost = generate_summary(video_title, video_author, transcription, transcription_errors, outline, 1, None, model)
                    total_cost += first_summary_cost
                    st.markdown("# Summary for Bullet 1")
                    st.markdown(first_summary)

                bullet_summaries = [first_summary]
                with st.spinner("Generating summaries for remaining bullets..."):
                    remaining_summaries = asyncio.run(generate_summaries_async(video_title, video_author, transcription, transcription_errors, outline, num_bullets, first_summary, model))
                    for i, (summary, cost) in enumerate(remaining_summaries, start=2):
                        bullet_summaries.append(summary)
                        total_cost += cost
                        st.markdown(f"# Summary for Bullet {i}")
                        st.markdown(summary)

                combined_summaries = "\n\n".join(bullet_summaries)

                with st.spinner("Generating TL;DR..."):
                    tldr, tldr_cost = generate_tldr(combined_summaries, model)
                    total_cost += tldr_cost

                st.markdown("## TL;DR")
                st.markdown(tldr)

                with st.spinner("Generating vocabulary..."):
                    vocabulary, vocab_cost = generate_vocabulary(transcription, transcription_errors, combined_summaries, model)
                    total_cost += vocab_cost

                st.markdown("## Key Vocabulary")
                st.markdown(vocabulary)

                file_name = f"{video_title}.md" if video_title else f"{video_id}.md"
                with open(file_name, "w") as file:
                    file.write(f"# {video_title}\n\n{tldr}\n\n## Key Vocabulary\n\n{vocabulary}\n\n{combined_summaries}")

                with open(file_name, "rb") as file:
                    st.download_button(
                        label="Download Markdown",
                        data=file,
                        file_name=file_name,
                        mime="text/markdown"
                    )
                
                st.markdown(f"# Total Cost: ${total_cost:.2f}")
        else:
            st.error("Invalid YouTube URL")

if __name__ == "__main__":
    main()