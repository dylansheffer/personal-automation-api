import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

local_url = "http://localhost:8000/youtube_notes/full_process"
deployed_url = "https://automate-the-suck-out-of-life.onrender.com/youtube_notes/full_process"

url = deployed_url  # Use this for the deployed version

params = {
    "model": "gpt-4o-mini"
}
data = {
    "url": "https://youtu.be/5tvztBs_VYc"
}
headers = {
    "X-API-Key": os.getenv("API_KEY")
}

print(f"Using API Key: {os.getenv('API_KEY')}")  # Add this line

# Add error handling and timeout
try:
    response = requests.post(url, params=params, json=data, headers=headers, timeout=180)
    response.raise_for_status()  # Raises an HTTPError for bad responses
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
    exit(1)

# Check the response content before parsing
if response.status_code == 200:
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response content: {response.text}")
        exit(1)
else:
    print(f"Request failed with status code: {response.status_code}")
    print(f"Response content: {response.text}")
    exit(1)

# Create directories if they don't exist
os.makedirs('notes', exist_ok=True)
os.makedirs('transcripts', exist_ok=True)

# Save the summary content to a markdown file in the notes folder
notes_file_path = os.path.join('notes', result['file_name'])
with open(notes_file_path, 'w') as f:
    f.write(result['summary'])

# Save the transcription to a file in the transcripts folder
transcript_file_name = os.path.splitext(result['file_name'])[0] + '_transcript.txt'
transcript_file_path = os.path.join('transcripts', transcript_file_name)
with open(transcript_file_path, 'w') as f:
    f.write(result['transcription'])

print(f"Transcription saved to {transcript_file_path}")
print(f"Summary content saved to {notes_file_path}")
print(f"Total cost: ${result['cost']:.6f}")