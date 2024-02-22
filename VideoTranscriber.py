import shutil

import whisper
import os
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
from PIL import ImageFont, ImageDraw, Image

#hello

import numpy as np
class VideoTranscriber:
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self):
        print('Transcribing video')
        print(self.audio_path)
        result = self.model.transcribe(self.audio_path)
        text = result["segments"][0]["text"]
        textsize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16 / 9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)].shape[1]
        width = width - (width * 0.60)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textsize[0] / len(text))

        for j in tqdm(result["segments"]):
            lines = []
            text = j["text"]
            end = j["end"]
            start = j["start"]
            total_frames = int((end - start) * self.fps)
            start = start * self.fps
            total_chars = len(text)
            words = text.split(" ")
            i = 0

            while i < len(words):
                words[i] = words[i].strip()
                if words[i] == "":
                    i += 1
                    continue
                length_in_pixels = len(words[i]) * self.char_width
                #490 is meant to be wi
                remaining_pixels = width - length_in_pixels
                line = words[i]

                while remaining_pixels > 0:
                    i += 1
                    if i >= len(words):
                        break
                    length_in_pixels = len(words[i]) * self.char_width
                    remaining_pixels -= length_in_pixels
                    if remaining_pixels < 0:
                        continue
                    else:
                        line += " " + words[i]

                line_array = [line, int(start), int(len(line) / total_chars * total_frames) + int(start)]
                start = int(len(line) / total_chars * total_frames) + int(start)
                lines.append(line_array)
                self.text_array.append(line_array)

        cap.release()
        print('Transcription complete')

    def extract_audio(self, output_audio_path='test_videos\\audio.mp3'):
        print('Extracting audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')

    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = width / height
        N_frames = 0

        font_path = "FONT/Frank.ttf"  # Path to your custom font
        font_size = 40  # Adjust the font size as needed
        font = ImageFont.truetype(font_path, font_size)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)]

            for i in self.text_array:
                if N_frames >= i[1] and N_frames <= i[2]:
                    text = i[0] + ""
                    words = text.split()
                    # print("entire words(sentence)", words)
                    # print("first word", words[0])

                    # Calculate text size
                    text_width = font.getmask(text).getbbox()[2]
                    text_height = font.getmask(text).getbbox()[3]

                    text_x = int((frame.shape[1] - text_width) / 2)
                    text_y = int(height / 2)

                    # Create PIL image
                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_image)

                    # Adding background color
                    bg_color = (0, 0, 0)  # Background color (black in this case)

                    # COMMENT 70 can be changed to any value to adjust the height of the text box
                    #draw.rectangle([(text_x, text_y), (text_x + text_width + 1, text_y + 35)], fill=bg_color)

                    x_offset = 0
                    for i in range(0, len(words)):
                        outline_width = 1.5  # Adjust the width of the outline as needed
                        outline_x = text_x + x_offset
                        outline_y = text_y

                        draw.text((outline_x - outline_width, outline_y), words[i], font=font, fill=(0, 0, 0))  # Left
                        draw.text((outline_x + outline_width, outline_y), words[i], font=font, fill=(0, 0, 0))  # Right
                        draw.text((outline_x, outline_y - outline_width), words[i], font=font, fill=(0, 0, 0))  # Up
                        draw.text((outline_x, outline_y + outline_width), words[i], font=font, fill=(0, 0, 0))  # Down


                        if i == (len(words)// 2):
                            text_color = (0, 255, 0)  # Specific color (red in this case)
                        else:
                            text_color = (255, 255,255)  # Default text color (white in this case)

                        # Add text with custom font
                        draw.text((text_x + x_offset, text_y), words[i], font=font, fill=text_color)
                        x_offset += font.getmask(words[i]).getbbox()[2] + 15  # Add space between words


                    # # Add text with custom font
                    # text_color = (255, 255, 255)  # Text color (white in this case)
                    # draw.text((text_x, text_y), text, font=font, fill=text_color)

                    # Convert PIL image to OpenCV format
                    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    break

            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1

        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        self.extract_frames(image_folder)

        print("Video saved at:", output_video_path)
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))

        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path)

        # this line deletes the frames folder
        shutil.rmtree(image_folder)


model_path = "base"
video_path = "downloaded_videos/1080pvideo.mp4"


output_video_path = "test_videos/output.mp4"

transcriber = VideoTranscriber(model_path, video_path)
transcriber.extract_audio()
transcriber.transcribe_video()
transcriber.create_video(output_video_path)
