from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import shutil
import os
import uuid
from app.model import run_pose_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/analyze-posture/")
async def analyze_posture(file: UploadFile = File(...)):
    input_filename = f"temp_{uuid.uuid4()}.mp4"
    output_filename = f"processed_{uuid.uuid4()}.mp4"
    output_path = os.path.join("static", output_filename)
    
    with open(input_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    final_classification, feedback = run_pose_model(input_filename, output_path)
    os.remove(input_filename)
    
    return {
        "video_url": f"http://localhost:8000/static/{output_filename}",
        "feedback": {
            "Classification": final_classification,
            "Comment": feedback
        }
    }
