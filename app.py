import requests
import json
import os

url = "http://localhost:8000/full_process"
params = {
    "model": "gpt-4o-mini"
}
data = {
    "url": "https://youtu.be/QghbHQq6eHw"
}
response = requests.post(url, params=params, json=data)
result = response.json()

# Save the result to a JSON file
with open('summary_result.json', 'w') as f:
    json.dump(result, f, indent=4)

print("Summary saved to summary_result.json")

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