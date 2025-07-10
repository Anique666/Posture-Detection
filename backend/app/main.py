from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from app.model import run_pose_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("temp_videos", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Backend is Live"}

@app.post("/analyze-posture/")
async def analyze_posture(file: UploadFile = File(...)):
    file_path = f"temp_videos/{file.filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = run_pose_model(file_path)

    os.remove(file_path)

    return {"feedback": result}
