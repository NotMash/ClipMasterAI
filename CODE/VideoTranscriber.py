import os
import shutil

import cv2
import numpy as np
import torch
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

from moviepy.video.VideoClip import ColorClip
import moviepy.video.fx.all as vfx
from moviepy.video.tools.drawing import color_split, blit

import whisper

from moviepy.config import change_settings
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


# Create a class to transcribe videos
class VideoTranscriber:
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path, device='cuda' if torch.cuda.is_available() else 'cpu')
        self.video_path = video_path
        self.audio_path = ''
        self.transcription = []
        self.fps = 0
        self.char_width = 0

    def extract_audio(self, output_audio_path='../output_videos/audio.mp3'):
        print('Extracting audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')

    def transcribe_video(self, words_per_frame):

        change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

        print('Transcribing video')
        result = self.model.transcribe(self.audio_path)
        segments = result["segments"]

        # Split each segment's text into smaller parts by whole words
        for segment in segments:
            text = segment['text']
            # Define your desired maximum length for each subsegment in words
            max_words_per_subsegment = words_per_frame  # for example, split every 10 words
            words = text.split()
            num_subsegments = (len(words) + max_words_per_subsegment - 1) // max_words_per_subsegment
            subsegment_length = len(words) // num_subsegments

            start_idx = 0
            for idx in range(num_subsegments):
                end_idx = min(start_idx + subsegment_length, len(words))
                subsegment = ' '.join(words[start_idx:end_idx])
                start_time = segment['start'] + idx * (segment['end'] - segment['start']) / num_subsegments
                end_time = segment['start'] + (idx + 1) * (segment['end'] - segment['start']) / num_subsegments
                self.transcription.append({
                    'id': segment['id'],
                    'start': start_time,
                    'end': end_time,
                    'text': subsegment,
                })
                start_idx = end_idx

        self.fps = VideoFileClip(self.video_path).fps
        print('Transcription complete')

    from moviepy.video.fx import all as vfx
    from moviepy.video.tools.drawing import color_split, blit

    def add_subtitles(self, output_video_path, font_path):
        video_clip = VideoFileClip(self.video_path)
        clips_with_subtitles = []

        for segment in self.transcription:
            start_time = segment['start']
            end_time = segment['end']
            #so it doesnt go over the video duration
            end_time = min(end_time, video_clip.duration)
            text = segment['text']

            # Calculate the duration of the subtitle
            duration = end_time - start_time

            # Create a TextClip with the subtitle
            subtitle_clip = TextClip(text, fontsize=65, color='white', align='center', font=font_path).set_duration(duration)

            # Add the subtitle at the specified start time
            clip_with_subtitle = CompositeVideoClip(
                [video_clip.subclip(start_time, end_time), subtitle_clip.set_position(('center', 0.465), relative=True)])

            clips_with_subtitles.append(clip_with_subtitle)

        # Concatenate all clips with subtitles
        final_clip = concatenate_videoclips(clips_with_subtitles)

        # Write the final video with subtitles
        final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac',
                                   temp_audiofile='temp-audio.m4a', remove_temp=True)

# Define paths
model_path = "small"
video_path = "../FINALVIDEO/final_video.mp4"
output_video_path = "../output_videos/output.mp4"
#
# # Initialize VideoTranscriber instance
transcriber = VideoTranscriber(model_path, video_path)
#
# # Extract audio from video
transcriber.extract_audio()
#
# # Transcribe video and align with audio
transcriber.transcribe_video(words_per_frame=5)
transcriber.add_subtitles(output_video_path, font_path="..//FONT//Frank.ttf")
#
# # Create video with highlighted spoken words
#transcriber.create_video(output_video_path)
