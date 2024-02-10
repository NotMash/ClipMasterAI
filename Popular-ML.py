import os
import json
import numpy as np
from googleapiclient.discovery import build
from transformers import BertTokenizer, BertForSequenceClassification
import re

# Function to fetch video segments data using YouTube API
def fetch_video_segments(video_id, api_key):
    try:
        # Build YouTube API service
        youtube = build('youtube', 'v3', developerKey=api_key)
        # Make API request to get video segments data
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            order='relevance',  # You may adjust the order based on your preference
            maxResults=10  # You may adjust the number of segments to fetch
        ).execute()
        return response.get('items', [])
    except Exception as e:
        print("Error fetching video segments data:", e)
        return None

# Function to extract relevant statistics from video segments data
def extract_segment_statistics(video_segments):
    segments_statistics = []
    for segment in video_segments:
        snippet = segment['snippet']
        segment_text = snippet['topLevelComment']['snippet']['textDisplay']
        # Here you can extract other relevant statistics for each segment, such as view count, like count, etc.
        # For demonstration purposes, we'll consider the length of the segment text as a statistic
        segment_statistics = len(segment_text)
        segments_statistics.append(segment_statistics)
    return segments_statistics

# Function to preprocess data and extract features
# Modify this function as needed to extract features from video segments
def preprocess_data(video_data):
    try:
        # Extract relevant features from video data
        # For demonstration purposes, we'll consider the length of the video title as a feature
        video_title = video_data['items'][0]['snippet']['title']
        features = len(video_title)
        return features
    except KeyError:
        print("Error: 'items' key not found in video data")
        return None

# Load pre-trained model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Function to predict viral content using pre-trained model
def predict_viral_content(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predicted_label = np.argmax(outputs.logits.detach().numpy())
    return predicted_label

# Function to fetch video data using YouTube API
def fetch_video_data(video_id, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        print("Video API response:", response)  # Print the response data
        return response
    except Exception as e:
        print("Error fetching video data:", e)
        return None

# Extract start and end times from segment text
def extract_times(segment_text):
    times = []
    pattern = r'(\d+:\d+)'
    matches = re.findall(pattern, segment_text)
    for i in range(0, len(matches), 2):
        start_time = matches[i]
        if i + 1 < len(matches):
            end_time = matches[i + 1]
        else:
            end_time = None
        times.append([start_time, end_time])
    return times
# Extract start and end times from segment text
def extract_times(segment_text):
    times = []
    pattern = r'(\d+:\d+)'
    matches = re.findall(pattern, segment_text)
    for i in range(0, len(matches), 2):
        start_time = matches[i]
        if i + 1 < len(matches):
            end_time = matches[i + 1]
        else:
            end_time = None
        times.append([start_time, end_time])
    return times
# Extract start and end times from segment text


# Example usage
if __name__ == "__main__":
    # Your YouTube API key
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YouTube API key not found in environment variables")
        exit(1)

    # Fetch video segments data
    video_id = 'WqJhvUYLRzk'
    video_segments = fetch_video_segments(video_id, api_key)
    if video_segments:
        # Extract relevant statistics from video segments
        segment_statistics = extract_segment_statistics(video_segments)
        if segment_statistics:
            # Determine the most viral segment based on the highest replay count
            most_viral_segment_index = np.argmax(segment_statistics)
            most_viral_segment_text = video_segments[most_viral_segment_index]['snippet']['topLevelComment']['snippet']['textDisplay']
            # Preprocess data (e.g., length of the video title)
            video_data = fetch_video_data(video_id, api_key)
            features = preprocess_data(video_data)
            # Example prediction
            text = 'Example video description or comments'
            predicted_label = predict_viral_content(text)
            print("Most viral segment text:", most_viral_segment_text)
            print("Predicted label:", predicted_label)

            # Extract start and end times from segment text
            times = extract_times(most_viral_segment_text)
            print("Start and end times:")
            for i, (start_time, end_time) in enumerate(times):
                print(f"Clip {i + 1}: Start - {start_time}, End - {end_time}")


        else:
            print("Error: No segment statistics extracted")
    else:
        print("Error: Failed to fetch video segments data from YouTube API")
