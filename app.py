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

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Cost per 1,000 tokens for different models
model_costs = {
    "gpt-4o": {
        "input": 0.005,
        "output": 0.015
    },
    "gpt-3.5-turbo": {
        "input": 0.0005,
        "output": 0.0015
    }
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

def get_transcription(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t['text'] for t in transcript])

def calculate_cost(usage, model):
    input_tokens = usage['prompt_tokens']
    output_tokens = usage['completion_tokens']
    input_cost = (input_tokens / 1000) * model_costs[model]['input']
    output_cost = (output_tokens / 1000) * model_costs[model]['output']
    return input_cost + output_cost

def generate_outline(video_title, transcription, model):
    conversation_outline = [
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "user", "content": f"Your task is to first read the document titled '{video_title}' and output a detailed numbered outline of the document section by section. Provide high-level overviews of the subjects within each section. Output the result as a JSON object with two properties: 'outline' for the detailed outline in ol markdown list resembling a table of contents with detailed subchapters, and 'num_bullets' for the number of parent bullet points.\n\n{transcription}"}
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

def generate_summary(video_title, transcription, outline, bullet_number, first_summary, model):
    conversation_summary = [
        {"role": "system", "content": "You are a helpful assistant designed to create structured summaries. You cover the essential information in your provided section and utilize complete sentences, lists, tables, quotes, etc to completely capture the original transcription."},
        {"role": "user", "content": f"Using this outline as a reference to ensure you're covering all the points mentioned in the outline for the video titled '{video_title}', your task is to create a detailed summary that DOES NOT exclude important details and examples mentioned in the source text. You must output in a structured Markdown output with a proper heading structure starting at h2. Use all markdown features that are relevant to your summary such as tables, quotes, sub headings, etc. Let's start with bullet {bullet_number}. **DO NOT** go beyond the bullet you are instructed to write. **DO NOT** output the number for the section title. **ONLY** output the summary for the bullet you are instructed to write. **DO NOT** output anything else.\n---\n\n## Video Outline\n{outline}\n\n## Video Transcription\n{transcription}\n\n"}
    ]
    if first_summary and bullet_number > 1:
        conversation_summary.append({"role": "assistant", "content": first_summary})
        conversation_summary.append({"role": "user", "content": f"Now, please summarize bullet {bullet_number} in a similar style."})
    
    response = openai.ChatCompletion.create(model=model, messages=conversation_summary)
    summary = response['choices'][0]['message']['content']
    
    return summary, calculate_cost(response['usage'], model)

async def generate_summaries_async(video_title, transcription, outline, num_bullets, first_summary, model):
    tasks = []
    for i in range(2, num_bullets + 1):
        tasks.append(asyncio.to_thread(generate_summary, video_title, transcription, outline, i, first_summary, model))
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

def main():
    st.title("YouTube Video Summarizer")

    model = st.selectbox("Choose the model", ["gpt-4o", "gpt-3.5-turbo"])

    youtube_url = st.text_input("Enter YouTube URL")

    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            st.video(youtube_url)

            if st.button("Summarize"):
                total_cost = 0.0

                with st.spinner("Fetching video title..."):
                    video_title = get_video_title(video_id)

                with st.spinner("Fetching transcription..."):
                    transcription = get_transcription(video_id)

                with st.spinner("Generating outline..."):
                    outline, num_bullets, outline_cost = generate_outline(video_title, transcription, model)
                    total_cost += outline_cost
                    st.markdown("# Outline")
                    st.markdown(outline)

                with st.spinner("Generating summary for bullet 1..."):
                    first_summary, first_summary_cost = generate_summary(video_title, transcription, outline, 1, None, model)
                    total_cost += first_summary_cost
                    st.markdown("# Summary for Bullet 1")
                    st.markdown(first_summary)

                bullet_summaries = [first_summary]
                with st.spinner("Generating summaries for remaining bullets..."):
                    remaining_summaries = asyncio.run(generate_summaries_async(video_title, transcription, outline, num_bullets, first_summary, model))
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

                file_name = f"{video_title}.md" if video_title else f"{video_id}.md"
                with open(file_name, "w") as file:
                    file.write(f"# {video_title}\n\n{tldr}\n\n{combined_summaries}")

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
