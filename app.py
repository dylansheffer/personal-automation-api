import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "http://localhost:8000/youtube_notes/full_process"
params = {
    "model": "gpt-4o-mini"
}
data = {
    "url": "https://www.youtube.com/watch?v=CVBpYfPKGlE"
}
headers = {
    "X-API-Key": os.getenv("API_KEY")
}
response = requests.post(url, params=params, json=data, headers=headers)
result = response.json()

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