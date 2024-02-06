from pytube import YouTube
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip

import os

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/magick"})


import ssl
from pytube import YouTube

ssl._create_default_https_context = ssl._create_unverified_context

# Function to download YouTube video
def download_youtube_video(youtube_url, output_path):
    yt = YouTube(youtube_url)
    yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    downloaded_video = yt.download(output_path)
    return downloaded_video


# Function to crop and resize video
def edit_video(video_path, start_time, end_time, resize_dimensions, additional_clip_path):
    # Load the main video clip
    video = VideoFileClip(video_path)
    # Crop the video
    video = video.subclip(start_time, end_time)
    # Resize the video
    video = video.resize(resize_dimensions)
    # Load the additional clip
    additional_clip = VideoFileClip(additional_clip_path)
    # Add the additional clip to the main video
    final_video = CompositeVideoClip([video, additional_clip])
    edited_video_path = "edited_video.mp4"
    final_video.write_videofile(edited_video_path)
    return edited_video_path

# Function to add subtitles to the video
def add_subtitles_to_video(video_path, subtitles_text):
    # Create a TextClip object for subtitles
    txt_clip = TextClip(subtitles_text, fontsize=24, color='white')
    txt_clip = txt_clip.set_position('bottom').set_duration(10)
    # Load the main video clip
    video = VideoFileClip(video_path)
    # Overlay the subtitles on the video
    final_video = CompositeVideoClip([video, txt_clip])
    final_video_path = "final_video_with_subtitles.mp4"
    final_video.write_videofile(final_video_path)
    return final_video_path

# Main automation function
def create_tiktok_video(youtube_url, start_time, end_time, resize_dimensions, additional_clip_path, subtitles_text):
    # Download the YouTube video
    downloaded_video = download_youtube_video(youtube_url, os.getcwd())
    # Crop and resize the video
    edited_video = edit_video(downloaded_video, start_time, end_time, resize_dimensions, additional_clip_path)
    # Add subtitles to the video
    final_video = add_subtitles_to_video(edited_video, subtitles_text)
    return final_video

# Example usage:
final_video = create_tiktok_video(
    youtube_url="https://www.youtube.com/watch?v=h5nRDUYtgJw",
    start_time=0,
    end_time=10,
    resize_dimensions=(720, 720),
    additional_clip_path="/Users/mash/PycharmProjects/pythonProject4/TikTok_ Minecraft COMPILATION.mp4",
    subtitles_text="This is a TikTok video created using Python!"
)

print(f"Created TikTok video: {final_video}")
