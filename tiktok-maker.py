from pytube import YouTube
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip

import os

from moviepy.config import change_settings
# C:\Program Files\ImageMagick-7.1.1-Q16-HDRI
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


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
# Function to crop, resize and stack videos vertically
def edit_video(youtube_video_path, additional_clip_path, output_resolution):
    # Load the main video clip, crop and resize to the top half of the output resolution
    youtube_video = VideoFileClip(youtube_video_path).resize(height=output_resolution[1] // 2)
    # Load the additional clip, crop and resize to the bottom half of the output resolution
    additional_clip = VideoFileClip(additional_clip_path).resize(height=output_resolution[1] // 2)

    # Stack the clips vertically
    final_video = CompositeVideoClip([youtube_video.set_position(("center", "top")),
                                      additional_clip.set_position(("center", "bottom"))],
                                     size=output_resolution)

    edited_video_path = "stacked_video.mp4"
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
# Function to create the final TikTok video
# Function to create the final TikTok video
def create_tiktok_video(youtube_url, start_time, end_time, additional_clip_path, subtitles_text,
                        output_resolution=(1920, 1080)):
    # Download the YouTube video
    downloaded_video_path = download_youtube_video(youtube_url, os.getcwd())

    # Crop the downloaded video between start_time and end_time
    youtube_video = VideoFileClip(downloaded_video_path).subclip(start_time, end_time).resize(
        height=output_resolution[1] // 2)

    # Load the additional clip and resize it
    additional_clip = VideoFileClip(additional_clip_path).subclip(start_time, end_time).resize(height=output_resolution[1] // 2)

    # Stack the clips vertically
    final_video = CompositeVideoClip([youtube_video.set_position(("center", "top")),
                                      additional_clip.set_position(("center", "bottom"))],
                                     size=output_resolution)

    edited_video_path = "stacked_video.mp4"
    final_video.write_videofile(edited_video_path)

    # Add subtitles to the video
    final_video_with_subtitles_path = add_subtitles_to_video(edited_video_path, subtitles_text)

    return final_video_with_subtitles_path


# Example usage:
final_video = create_tiktok_video(
    youtube_url="https://www.youtube.com/watch?v=h5nRDUYtgJw",
    start_time=30,
    end_time=35,
    additional_clip_path="C:\\Users\\Ghafo\\Desktop\\projects\\Tiktok\\TikTok_ Minecraft COMPILATION.mp4",
    #additional_clip_path="C:\\Users\\Ghafo\\Desktop\\projects\\Tiktok\\TikTok_ Minecraft COMPILATION.mp4",
    subtitles_text="This is a TikTok video created using Python!"
)
#"C:\\Users\\Ghafo\\Desktop\\projects\\Tiktok\\TikTok_ Minecraft COMPILATION.mp4"


print(f"Created TikTok video: {final_video}")


#add captions
#choose the best intervals
#