import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [summary, setSummary] = useState(null);

  const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";

  const handleUpload = (e) => {
    setFile(e.target.files[0]);
    setVideoUrl(null);
    setSummary(null);
  };

  const handleSubmit = async () => {
    if (!file) return alert("Please upload a video.");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BASE_URL}/analyze-posture/`,{
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setVideoUrl(data.video_url);
    setSummary(data.feedback);
  };

  return (
    <div className="container">
      <h1 className="heading">Posture Detection</h1>

      <div className="content">
        <div className="left">
          <p>
            This model uses <strong>MediaPipe</strong> and <strong>OpenCV</strong> to analyze posture
            frame-by-frame and classify the video as either <em>Sitting</em> or <em>Squatting</em>.
          </p>
        </div>
        <div className="right">
          <input type="file" accept="video/*" onChange={handleUpload} />
          <button onClick={handleSubmit}>Submit</button>
        </div>
      </div>

      {videoUrl && (
        <div className="video-preview">
          <video key={videoUrl} src={videoUrl} controls width="600" />
        </div>
      )}

      {summary && (
        <div className="summary">
          <h2>Summary</h2>
          <ul>
            <li>
              <strong>Posture Type:</strong> {summary.Classification}
            </li>
            <li>
              <strong>Feedback:</strong> {summary.Comment}
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
