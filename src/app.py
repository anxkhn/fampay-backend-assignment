import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Retrieve the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Define the publish time (10:30 AM on April 7th, 2024)
publish_time = datetime(2024, 4, 7, 10, 30)

# Define the time to be one hour before the publish time
published_after = publish_time - timedelta(hours=1)

# Format the publish time as RFC 3339 timestamp
published_after = published_after.isoformat() + 'Z'

# Build the YouTube Data API service
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Call the search.list method to retrieve videos
search_response = youtube.search().list(
    part='snippet',
    q='search_query_here',
    type='video',
    order='date',
    publishedAfter=published_after,
    maxResults=50
).execute()

# Print the search results
print(search_response)
