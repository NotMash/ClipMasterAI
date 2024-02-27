import shutil
import os
import cv2
import numpy as np
import torch
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip
from PIL import ImageFont, ImageDraw, Image
from tqdm import tqdm
import whisper

# Create a class to transcribe videos
class VideoTranscriber:
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path, device='cuda' if torch.cuda.is_available() else 'cpu')
        self.video_path = video_path
        self.audio_path = ''
        self.transcription = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self, words_per_frame):
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

    def highlight_word(self, frame, text, highlight_index):
        font_path = "../FONT/Frank.ttf"  # Path to your custom font
        max_font_size = 60  # Maximum font size
        min_font_size = 20  # Minimum font size
        margin = 50

        # Initialize font size
        font_size = max_font_size

        # Create font object
        font = ImageFont.truetype(font_path, font_size)

        # Split text into words
        words = text.split()

        # Calculate total text width
        total_text_width = sum([font.getmask(word).getbbox()[2] for word in words]) + (len(words) - 1) * 15

        # Check if total text width exceeds frame width
        if total_text_width > frame.shape[1] - 2*margin:
            #print("INSIDE HEREEE")
            # Reduce font size to fit text within frame
            font_size = max(min_font_size, int((max_font_size * (frame.shape[1] - 2 * margin)) / total_text_width))
            font = ImageFont.truetype(font_path, font_size)

            # Recalculate total text width with reduced font size

        total_text_width = sum([font.getmask(word).getbbox()[2] for word in words]) + (len(words) - 1) * 15

        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        # Calculate starting x-coordinate to center text
        start_x = int((frame.shape[1] - total_text_width) / 2)

        x_offset = 0

        for i, word in enumerate(words):
            text_width = font.getmask(word).getbbox()[2]
            text_height = font.getmask(word).getbbox()[3]

            text_x = start_x + x_offset
            text_y = int(frame.shape[0] / 2)

            if i == highlight_index:
                text_color = (0, 255, 0)  # Highlight color (green)
            else:
                text_color = (255, 255, 255)  # Default text color (white)

            draw.text((text_x, text_y), word, font=font, fill=text_color)
            x_offset += text_width + 15  # Add space between words

        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def extract_frames(self, output_folder):
        print('Extracting frames')
        video = cv2.VideoCapture(self.video_path)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        aspect_ratio = width / height
        frame_count = 0

        for _ in tqdm(range(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame = video.read()
            if not ret:
                break

            speaking = False  # Flag to track if speaking is detected in the audio segment
            for segment in self.transcription:
                start_time = segment["start"]
                end_time = segment["end"]
                words = segment["text"].split()
                total_frames = int((end_time - start_time) * self.fps)
                start_frame = int(start_time * self.fps)

                # Check if the current frame falls within the current transcription segment
                if start_frame <= frame_count < start_frame + total_frames:
                    elapsed_time = (frame_count - start_frame) / self.fps
                    #using elapsed percentage to work out the highlightation
                    segment_duration = end_time - start_time
                    elapsed_percentage = elapsed_time / segment_duration + 0.2
                    word_index = int(elapsed_percentage * len(words))
                    word_index = min(max(0, word_index), len(words) - 1)
                    frame = self.highlight_word(frame, segment["text"], word_index)
                    speaking = True  # Set speaking flag to True if segment is found
                    break

            if not speaking:  # If no speech detected, show paused frame
                frame = self.highlight_word(frame, "", 0)

            cv2.imwrite(os.path.join(output_folder, f"{frame_count}.jpg"), frame)
            frame_count += 1

        video.release()
        print('Frames extracted')

    def extract_audio(self, output_audio_path='output_videos/audio.mp3'):
        print('Extracting audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        output_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.extract_frames(output_folder)

        images = [img for img in os.listdir(output_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))

        frame = cv2.imread(os.path.join(output_folder, images[0]))
        height, width, _ = frame.shape

        clip = ImageSequenceClip([os.path.join(output_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path)

        shutil.rmtree(output_folder)
        print("Video saved at:", output_video_path)

# Define paths
# model_path = "small"
# video_path = "../downloaded_videos/ChunksPodcast.mp4"
# output_video_path = "../output_videos/output.mp4"
#
# # Initialize VideoTranscriber instance
# transcriber = VideoTranscriber(model_path, video_path)
#
# # Extract audio from video
# transcriber.extract_audio()
#
# # Transcribe video and align with audio
# transcriber.transcribe_video(words_per_frame=5)
#
# # Create video with highlighted spoken words
# transcriber.create_video(output_video_path)
