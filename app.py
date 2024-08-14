import requests
import json

url = "http://localhost:8000/full_process"
params = {
    "model": "gpt-4o-mini"
}
data = {
    "url": "https://youtu.be/9KqrnBiyBQ8"
}
response = requests.post(url, params=params, json=data)
result = response.json()

# Save the result to a file
with open('summary_result.json', 'w') as f:
    json.dump(result, f, indent=4)

print("Summary saved to summary_result.json")