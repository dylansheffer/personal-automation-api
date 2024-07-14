import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Global variable to store conversation history
conversation_history = []
total_cost = 0.0

# Cost per 1,000 tokens
input_cost_per_1000_tokens = 5 / 1000
output_cost_per_1000_tokens = 15 / 1000

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

def get_transcription(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t['text'] for t in transcript])

def calculate_cost(usage):
    input_tokens = usage['prompt_tokens']
    output_tokens = usage['completion_tokens']
    input_cost = (input_tokens / 1000) * input_cost_per_1000_tokens
    output_cost = (output_tokens / 1000) * output_cost_per_1000_tokens
    return input_cost + output_cost

def generate_outline(text, model):
    global conversation_history, total_cost
    conversation_outline = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Your task is to first read the document and output a detailed numbered outline of the document section by section. Provide high-level overviews of the subjects within each section. At the end output the number of parent bullet points like this: '14 bullets'\n\n{text}"}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_outline)
    outline = response['choices'][0]['message']['content']
    
    # Calculate and accumulate cost
    total_cost += calculate_cost(response['usage'])
    
    # Check if the search result is not None
    match = re.search(r'(\d+) bullets', outline)
    if match:
        num_bullets = int(match.group(1))
    else:
        num_bullets = 0  # or handle the error as needed
    
    conversation_history = conversation_outline + [{"role": "assistant", "content": outline}]
    return outline, num_bullets

def generate_summary(text, bullet_number, model):
    global conversation_history, total_cost
    conversation_summary = conversation_history + [
        {"role": "user", "content": f"Using this outline as a reference, your task is to create a concise summary that DOES NOT exclude important details and examples mentioned in the source text. If information from the outline is unclear or not present in the document, output 'I Don't Know' in bold text, so I will see it. You must output in a structured Markdown output with a proper heading structure and use of tables for tabular data.\n\nLet's start with bullet {bullet_number}. **DO NOT** go beyond the bullet you are instructed to write. **DO NOT** output the number for the section title."}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_summary)
    summary = response['choices'][0]['message']['content']
    
    # Calculate and accumulate cost
    total_cost += calculate_cost(response['usage'])
    
    return summary

async def generate_summaries_async(text, num_bullets, model):
    tasks = []
    for i in range(2, num_bullets + 1):
        tasks.append(asyncio.to_thread(generate_summary, text, i, model))
    return await asyncio.gather(*tasks)

def generate_tldr(text, model):
    global total_cost
    conversation_tldr = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Create a TL;DR of the provided text. H2 for the TL;DR heading.\n\n---\n\n{text}"}
    ]
    response = openai.ChatCompletion.create(model=model, messages=conversation_tldr)
    tldr = response['choices'][0]['message']['content']
    
    # Calculate and accumulate cost
    total_cost += calculate_cost(response['usage'])
    
    conversation_tldr += {"role": "assistant", "content": tldr},
    response_punchy = openai.ChatCompletion.create(model=model, messages=conversation_tldr)
    
    # Calculate and accumulate cost
    total_cost += calculate_cost(response_punchy['usage'])
    
    return response_punchy['choices'][0]['message']['content']

def main():
    st.title("YouTube Video Summarizer")

    model = st.selectbox("Choose the model", ["gpt-4o", "gpt-3.5-turbo"])

    youtube_url = st.text_input("Enter YouTube URL")

    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            st.video(youtube_url)

            if st.button("Summarize"):
                with st.spinner("Fetching video title..."):
                    video_title = get_video_title(video_id)

                with st.spinner("Fetching transcription..."):
                    transcription = get_transcription(video_id)

                with st.spinner("Generating outline..."):
                    outline, num_bullets = generate_outline(transcription, model)
                    st.markdown("### Outline")
                    st.markdown(outline)

                with st.spinner("Generating summary for bullet 1..."):
                    first_summary = generate_summary(transcription, 1, model)
                    st.markdown("### Summary for Bullet 1")
                    st.markdown(first_summary)

                bullet_summaries = [first_summary]
                with st.spinner("Generating summaries for remaining bullets..."):
                    remaining_summaries = asyncio.run(generate_summaries_async(transcription, num_bullets, model))
                    bullet_summaries.extend(remaining_summaries)
                    for i, summary in enumerate(remaining_summaries, start=2):
                        st.markdown(f"### Summary for Bullet {i}")
                        st.markdown(summary)

                combined_summaries = "\n\n".join(bullet_summaries)

                with st.spinner("Generating TL;DR..."):
                    tldr = generate_tldr(combined_summaries, model)

                st.markdown("## TL;DR")
                st.markdown(tldr)

                file_name = f"{video_title}.md" if video_title else f"{video_id}.md"
                with open(file_name, "w") as file:
                    file.write(tldr + "\n\n" + combined_summaries)

                with open(file_name, "rb") as file:
                    st.download_button(
                        label="Download Markdown",
                        data=file,
                        file_name=file_name,
                        mime="text/markdown"
                    )
                
                st.markdown(f"### Total Cost: ${total_cost:.2f}")
        else:
            st.error("Invalid YouTube URL")

if __name__ == "__main__":
    main()


# ToDO
# update the toggle so the cost calculation changes when the model changes
# update the prompts so they output with consistent headings and have better system prompts and see what's up with the extra lines and the "I Don't Knows". I would also like to not have any other output other than the markdown
# Make the outline a step that can be regenerated instead of it auto going to the next step