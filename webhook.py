import requests

# Replace with your actual Make Webhook URL
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/7troe5wj1k92ydltc39rv7l6ipj7okso"

# Define the YouTube link you want to send
youtube_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example link, replace with your own

# Prepare the data payload
data = {
    "youtube_link": youtube_link
}

# Define request headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(MAKE_WEBHOOK_URL, headers=headers, json=data)

# Check the response
if response.status_code == 200:
    print("✅ Successfully sent data to the webhook!")
else:
    print(f"❌ Failed to send data. Status Code: {response.status_code}, Response: {response.text}")
