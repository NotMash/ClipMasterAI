import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [youtubeUrl, setYoutubeUrl] = useState("");
    const [startTime, setStartTime] = useState(0);
    const [endTime, setEndTime] = useState(10);
    const [modelPath, setModelPath] = useState("base");
    const [wordPerFrame, setWordPerFrame] = useState(5);

    const handleCreateTikTok = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/create_tiktok', {
                youtube_url: youtubeUrl,
                start_time: startTime,
                end_time: endTime,
                model_path: modelPath,
                word_per_frame: wordPerFrame
            });
            console.log("TikTok video created:", response.data.message);
        } catch (error) {
            console.error('Error creating TikTok:', error);
        }
    };

    const handleDownloadVideo = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/download_video', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'tiktok_video.mp4');
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Error downloading video:', error);
        }
    };

    return (
        <div className="App">
            <h1>Create TikTok</h1>
            <div>
                <label htmlFor="youtubeUrl">YouTube URL:</label>
                <input
                    type="text"
                    id="youtubeUrl"
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                />
            </div>
            <div>
                <label htmlFor="startTime">Start Time (seconds):</label>
                <input
                    type="number"
                    id="startTime"
                    value={startTime}
                    onChange={(e) => setStartTime(parseInt(e.target.value))}
                />
            </div>
            <div>
                <label htmlFor="endTime">End Time (seconds):</label>
                <input
                    type="number"
                    id="endTime"
                    value={endTime}
                    onChange={(e) => setEndTime(parseInt(e.target.value))}
                />
            </div>
            <div>
                <label htmlFor="modelPath">Model Path:</label>
                <input
                    type="text"
                    id="modelPath"
                    value={modelPath}
                    onChange={(e) => setModelPath(e.target.value)}
                />
            </div>
            <div>
                <label htmlFor="wordPerFrame">Words Per Frame:</label>
                <input
                    type="number"
                    id="wordPerFrame"
                    value={wordPerFrame}
                    onChange={(e) => setWordPerFrame(parseInt(e.target.value))}
                />
            </div>
            <button onClick={handleCreateTikTok}>Create TikTok</button>
            <button onClick={handleDownloadVideo}>Download TikTok Video</button>
        </div>
    );
}

export default App;