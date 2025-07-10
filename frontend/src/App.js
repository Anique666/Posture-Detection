import React, { useState, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [summary, setSummary] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef();

  const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";

  const handleUpload = (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    setVideoUrl(null);
    setSummary(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setVideoUrl(null);
      setSummary(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleButtonClick = () => {
    inputRef.current.click();
  };

  const handleSubmit = async () => {
    if (!file) return alert("Please upload a video.");

    setLoading(true);
    setVideoUrl(null);
    setSummary(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${BASE_URL}/analyze-posture/`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setVideoUrl(data.video_url);
      setSummary(data.feedback);
    } catch (err) {
      alert("An error occurred while processing the video.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fancy-bg">
      <div className="fancy-card">
        <h1 className="fancy-heading">Posture Analyzer</h1>
        <p className="fancy-desc">
          Upload a video to analyze your posture using{" "}
          <strong>MediaPipe</strong> and <strong>OpenCV</strong>.
          <br />
          The model will classify your posture as{" "}
          <em>Sitting</em> or <em>Squatting</em> and provide feedback.
        </p>

        <div
          className={`upload-area ${dragActive ? "drag-active" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleButtonClick}
        >
          {file ? (
            <span className="file-name">{file.name}</span>
          ) : (
            <span>
              Drag and drop a video or{" "}
              <span className="upload-link">browse files</span>
            </span>
          )}
          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            onChange={handleUpload}
            style={{ display: "none" }}
          />
        </div>

        <button
          className="fancy-btn"
          onClick={handleSubmit}
          disabled={!file || loading}
        >
          {loading ? (
            <>
              <span className="loader"></span>
              <span className="loading-text">Processing...</span>
            </>
          ) : (
            "Analyze Posture"
          )}
        </button>

        {videoUrl && (
          <div className="video-preview">
            <video controls>
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {summary && (
          <div className="summary">
            <h2>Summary</h2>
            <div className="summary-item">
              <strong>Posture Type :</strong> {summary.Classification}
            </div>
            <div className="summary-item">
              <strong>Feedback :</strong> {summary.Comment}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
