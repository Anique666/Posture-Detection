# Posture Detection

A full-stack application for detecting and analyzing posture from videos. This project includes a Python backend for processing videos and a React frontend for user interaction.

## Directory Structure

```
Posture-Detection/
├── backend/                # Python backend
│   ├── app/                # Backend application code
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── model.py
│   ├── static/             # Processed video files
│   ├── temp_videos/        # Temporary video storage
│   ├── requirements.txt    # Python dependencies
│   ├── runtime.txt         # Runtime version info
│   └── Dockerfile          # Docker setup for backend
├── frontend/               # React frontend
│   ├── public/             # Static public assets
│   ├── src/                # React source code
│   ├── build/              # Production build output
│   ├── package.json        # Frontend dependencies
│   └── README.md           # Frontend-specific docs
```

## Key Features

- Upload videos for posture analysis
- Automated posture detection using rule based logic
- Download processed videos with posture feedback
- Modern, responsive web interface


## Tech Stack

**Backend:**
- FastAPI
- OpenCV and MediaPipe for Video Processing
- Docker for Deployement 

**Frontend:**
- React
- JavaScript
- CSS

## Getting Started

### Prerequisites
- Git
- Node.js & npm (for frontend)
- Python 3.12 (for backend)
- Docker (optional)

### Clone the Repository

```sh
git clone https://github.com/your-username/Posture-Detection.git
cd Posture-Detection
```

### Backend Setup

```sh
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Frontend Setup

```sh
cd frontend
npm install
npm start
```

The frontend will run on [http://localhost:3000](http://localhost:3000) and the backend on [http://localhost:5000](http://localhost:5000).

---

