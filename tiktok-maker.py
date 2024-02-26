import os
from pytube import YouTube
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from concurrent.futures import ThreadPoolExecutor
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class TikTokVideoCreator:
    def __init__(self, youtube_url, start_time, end_time, additional_clip_path, watermarked_text,
                 output_resolution=(1080, 1920)):
        self.youtube_url = youtube_url
        self.start_time = start_time
        self.end_time = end_time
        self.additional_clip_path = additional_clip_path
        self.watermarked_text = watermarked_text
        self.output_resolution = output_resolution

    def download_youtube_video(self, output_path):
        yt = YouTube(self.youtube_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        downloaded_video_path = stream.download(output_path)
        return downloaded_video_path

    def resize_video(self, video_path, output_height):
        video = VideoFileClip(video_path)
        resized_video = video.subclip(self.start_time, self.end_time).resize(height=output_height)
        return resized_video

    def add_watermark_to_video(self, video):
        watermark_text_clip = TextClip(self.watermarked_text, fontsize=40, color='white').set_duration(video.duration)
        watermark_text_clip = watermark_text_clip.set_position((0.1, 0.8), relative=True).set_opacity(0.5)
        final_video = CompositeVideoClip([video, watermark_text_clip])
        return final_video

    def create_tiktok_video(self):
        downloaded_video_path = self.download_youtube_video("../downloaded_videos")
        with ThreadPoolExecutor() as executor:
            resized_video_future = executor.submit(self.resize_video, downloaded_video_path, self.output_resolution[1] // 2)
            additional_clip_future = executor.submit(self.resize_video, self.additional_clip_path, self.output_resolution[1] // 2)
            resized_video = resized_video_future.result()
            additional_clip = additional_clip_future.result()

        additional_clip = additional_clip.set_audio(None)
        final_video = CompositeVideoClip([resized_video.set_position(("center", "top")),
                                          additional_clip.set_position(("center", "bottom"))],
                                         size=self.output_resolution)

        # Add watermark to the final video
        final_video_with_watermark = self.add_watermark_to_video(final_video)

        final_video_path = "../FINALVIDEO/final_video.mp4"
        final_video_with_watermark.write_videofile(final_video_path, codec="libx264", temp_audiofile="temp-audio.m4a", remove_temp=True, audio_codec="aac")
        return final_video_path


# Create directory for final video
os.makedirs("../FINALVIDEO", exist_ok=True)

# Example usage:
tiktok_creator = TikTokVideoCreator(
    youtube_url="https://www.youtube.com/watch?v=RoBRy8LHbEc",
    start_time=100,
    end_time=120,
    additional_clip_path="../downloaded_videos/GTA-CLIP-1.mp4",
    watermarked_text="@PLACEHOLDER"
)
final_video = tiktok_creator.create_tiktok_video()

print(f"Created TikTok video: {final_video}")