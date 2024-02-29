import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [youtubeUrl, setYoutubeUrl] = useState("");
    const [startTime, setStartTime] = useState(0);
    const [endTime, setEndTime] = useState(10);
    const [modelPath, setModelPath] = useState("base");
    const [wordPerFrame, setWordPerFrame] = useState(5);
    const [loading, setLoading] = useState(false);
    const [videoCreated, setVideoCreated] = useState(false);
    const [showDownloadButton, setShowDownloadButton] = useState(false);
    const [tikTokCompleted, setTikTokCompleted] = useState(false); // New state variable

    // Determine base URL based on the environment
    const hostname = window.location.hostname;
    const baseURL = hostname === 'localhost' ? 'http://localhost:5001' : `http://${hostname}:5001`;

    const handleCreateTikTok = async () => {
    try {
        setLoading(true);
        const response = await axios.post(`${baseURL}/create_tiktok`, {
            youtube_url: youtubeUrl,
            start_time: startTime,
            end_time: endTime,
            model_path: modelPath,
            word_per_frame: wordPerFrame
        });
        console.log("TikTok video created:", response.data.message);
        setVideoCreated(true);
        setTimeout(() => {
            setShowDownloadButton(true); // Show download button after 2 seconds
            setTikTokCompleted(true); // Set completion status to true
        }, 2000);
    } catch (error) {
        console.error('Error creating TikTok:', error);
    } finally {
        setLoading(false);
    }
};

    const handleDownloadVideo = async () => {
        try {
            const response = await axios.get(`${baseURL}/download_video`, { responseType: 'blob' });
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

    // Function to reset state and allow creation of TikTok again
    const resetTikTokCreation = () => {
        setVideoCreated(false);
        setShowDownloadButton(false);
        setTikTokCompleted(false); // Reset completion status
    };

   return (
    <div className="App">
        {loading && <div className="loading-bar"></div>}
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
        <button onClick={handleCreateTikTok} disabled={loading || videoCreated || tikTokCompleted}>Create TikTok</button>
        {loading && <p>Loading...</p>}
        {showDownloadButton && <button onClick={handleDownloadVideo}>Download TikTok Video</button>}
        <button onClick={resetTikTokCreation}>Reset TikTok Creation</button> {/* Add a reset button */}
    </div>
    );
}

export default App;
