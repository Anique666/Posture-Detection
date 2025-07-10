import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/analyze-posture/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setFeedback(data.feedback);
    } catch (err) {
      console.error("Error uploading:", err);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Posture Detection</h1>
      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload}>Analyze</button>

      {loading && <p>Analyzing...</p>}

      {feedback && (
        <div>
          <h3>Result:</h3>
          {typeof feedback === "string" ? (
            <p>{feedback}</p>
          ) : (
            Object.entries(feedback).map(([key, value]) => (
              <p key={key}>
                <strong>{key}:</strong> {value}
              </p>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default App;
