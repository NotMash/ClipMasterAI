
from CODE.tiktokMaker import TikTokVideoCreator
from CODE.VideoTranscriber import VideoTranscriber

#sample usage of the TikTokVideoCreator and

def main():
    # Prompt user for inputs
    youtube_url = input("Enter the YouTube URL: ")
    start_time = int(input("Enter the start time (in seconds): "))
    end_time = int(input("Enter the end time (in seconds): "))
    model_path = input("Enter the model path: ")
    word_per_frame = int(input("Enter the number of words per frame: "))



    tiktok_creator = TikTokVideoCreator(
        youtube_url=youtube_url,
        start_time=start_time,
        end_time=end_time,
        additional_clip_path="../downloaded_videos/GTA-CLIP-1.mp4",
        watermarked_text="@PLACE"
    )

    final_video = tiktok_creator.create_tiktok_video()
    print(f"TikTok video created: {final_video}")

    # Example usage of VideoTranscriber
    transcriber = VideoTranscriber(model_path=model_path, video_path="../FINALVIDEO/final_video.mp4")
    transcriber.extract_audio(output_audio_path="../output_videos/audio.mp3")

    transcriber.transcribe_video(words_per_frame=word_per_frame)

    transcriber.create_video(output_video_path="../output_videos/output.mp4")

if __name__ == "__main__":
    main()
