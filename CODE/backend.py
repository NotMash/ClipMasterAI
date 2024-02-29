from flask import Flask, request, jsonify, send_file
from tiktokMaker import TikTokVideoCreator
from VideoTranscriber import VideoTranscriber
import logging
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

@app.route("/create_tiktok", methods=["POST"])
def create_tiktok():
    logging.debug("Received request to create TikTok video.")
    data = request.json
    logging.debug("Request data: %s", data)
    youtube_url = data.get("youtube_url")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    model_path = data.get("model_path")
    word_per_frame = data.get("word_per_frame")

    try:
        # Use the provided parameters to create TikTok video and transcribe it
        tiktok_creator = TikTokVideoCreator(
            youtube_url=youtube_url,
            start_time=start_time,
            end_time=end_time,
            additional_clip_path="../downloaded_videos/GTA-CLIP-1.mp4",
        )
        final_video = tiktok_creator.create_tiktok_video()

        transcriber = VideoTranscriber(model_path=model_path, video_path="../FINALVIDEO/final_video.mp4")
        transcriber.extract_audio(output_audio_path="../output_videos/audio.mp3")
        transcriber.transcribe_video(words_per_frame=word_per_frame)
        transcriber.create_video(output_video_path="../output_videos/output.mp4")

        logging.debug("TikTok video created successfully.")
        return jsonify({"message": "TikTok video created and transcribed successfully."})

    except Exception as e:
        logging.error("Error creating TikTok video: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/download_video", methods=["GET"])
def download_video():
    logging.debug("Received request to download video.")
    return send_file("../output_videos/output.mp4", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
