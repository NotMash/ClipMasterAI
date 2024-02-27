import joblib
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline

from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
import numpy as np
from googleapiclient.discovery import build
#from dateutil.parser import parse as parse_duration
from isoduration import parse_duration
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
        # segment_text = snippet['topLevelComment']['snippet']['textDisplay']
        # Here you can extract other relevant statistics for each segment, such as view count, like count, etc.
        # For demonstration purposes, we'll consider the length of the segment text as a statistic
        # segment_statistics = len(segment_text)
        if 'title' in snippet:
            # Extract relevant statistics from the snippet's title
            segment_statistics = len(snippet['title'])
            segments_statistics.append(segment_statistics)
        else:
            # If the title is missing, consider the statistic as 0
            segments_statistics.append(0)
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
# model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')



# Function to predict viral content using pre-trained model
def predict_viral_content(model, text):

    if isinstance(text, list):
        # Convert list of strings to a single string
        text = ' '.join(text)

    #####################################################################################################################

    # emoji = {"anger": "😠", "disgust": "🤮", "fear": "😨😱", "happy": "🤗", "joy": "😂", "neutral": "😐",
    #                        "sad": "😔", "sadness": "😔", "shame": "😳", "surprise": "😮"}
    # results = model.predict([text])
    # probability = model.predict_proba([text])
    #
    # print("text: "+ text)
    # print("---results: "+ results+ " "+ emoji[results[0]])
    # print("---probability: ", (np.max(probability)))
    # print(" ")

    #####################################################################################################################

    results = model(text)
    # print("text: ", text)
    # print("prediction ", results)

    # inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    # outputs = model(**inputs)
    # print("----outputs:", outputs)
    # predicted_label = np.argmax(outputs.logits.detach().numpy())
    # return predicted_label

    return results

# Function to fetch video data using YouTube API
def fetch_video_data(video_id, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
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

def split_video_into_segments(response, transcript_data, lengthOfClip):
    try:
        duration_str = response['items'][0]['contentDetails']['duration']

        # Remove leading 'PT' from duration string
        duration_str = duration_str[2:]

        # Initialize hours, minutes, and seconds
        hours, minutes, seconds = 0, 0, 0

        # Parse duration string to get hours, minutes, and seconds
        if 'H' in duration_str:
            hours, duration_str = duration_str.split('H')
            hours = int(hours)
        if 'M' in duration_str:
            minutes, duration_str = duration_str.split('M')
            minutes = int(minutes)
        if 'S' in duration_str:
            seconds = duration_str.replace('S', '')
            seconds = int(seconds)

        # Convert duration to seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds

        # Define segment length (e.g., 60 seconds)
        segment_length_seconds = lengthOfClip

        # Split video into segments
        segments = []
        for start_time in range(0, total_seconds, segment_length_seconds):
            end_time = min(start_time + segment_length_seconds, total_seconds)
            segment_text = []
            for segment in transcript_data:
                segment_start = segment['start']
                segment_end = segment['start'] + segment['duration']
                if segment_start >= start_time and segment_end <= end_time:
                    segment_text.append(segment['text'])
            segments.append({'start_time': start_time, 'end_time': end_time, 'text': segment_text})

        return segments

    except Exception as e:
        print("Error splitting video into segments:", e)
        return None


def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # youtube = build('youtube', 'v3', developerKey=api_key)
        # captions = youtube.captions().list(
        #     part='snippet',
        #     videoId=video_id
        # ).execute()
        #
        # transcript_text = ""
        # for caption in captions['items']:
        #     caption_id = caption['id']
        #     transcript = youtube.captions().download(
        #         id=caption_id,
        #         tfmt='ttml'
        #     ).execute()
        #     transcript_text += transcript.decode('utf-8')  # Assuming the transcript is in UTF-8 format
        #
        return transcript

    except Exception as e:
        print("Error fetching transcript:", e)
        return None



# Example usage
if __name__ == "__main__":
    tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
    model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")


    # Your YouTube API key
    api_key = "AIzaSyAP3SwgXU_I5mUXYpuoRbV-nxzn5zVYZUY"
    if not api_key:
        print("Error: YouTube API key not found in environment variables")
        exit(1)

    # Fetch video segments data
    video_id = 'SNFvgniAPz4'
    video_data = fetch_video_data(video_id, api_key)
    if video_data:
        entire_transcript = fetch_transcript(video_id)
        #print("here is the transcript")
        #print(entire_transcript)

        # Split video into segments (e.g., time intervals or sliding windows)
        video_segments = split_video_into_segments(video_data, entire_transcript, lengthOfClip=45)
        #print(video_segments)
        if video_segments:
            # Predict virality for each segment
            segment_virality_scores = []
            count = 0
            model = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
            for segment in video_segments:
                segment_text = segment['text']  # Adjusted segment text extraction
                # print(count)
                # print("Start time:", segment['start_time'])
                # print("End time:", segment['end_time'])
                predicted_label = predict_viral_content(model, segment_text)
                #print("Predicted label:", predicted_label)
                segment_virality_scores.append(predicted_label)
                count += 1

            #sort my predicted labelled clips and remove the ones that are below x threshold

            sorted_scores = sorted(segment_virality_scores, key=lambda x: x['score'], reverse=True)
            print(sorted_scores)

            # print("Segment virality scores:", segment_virality_scores)


            # Select the most viral segment
            # most_viral_segment_index = np.argmax(segment_virality_scores)
            # best_segment = video_segments[most_viral_segment_index]
            # print("Best segment:", best_segment)
            #
            # # Extract start and end times from the best segment
            # start_time = best_segment['start_time']
            # end_time = best_segment['end_time']
            # print("Start time:", start_time)
            # print("End time:", end_time)
        else:
            print("Error: Failed to split video into segments")

    else:
        print("Error: Failed to fetch video data from YouTube API")