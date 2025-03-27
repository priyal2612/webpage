from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import os
import uuid
import uvicorn
from amazonnova import extract_frames, process_video_frames  # Ensure this file exists

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_FRAMES_DIR = "output_frames"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_FRAMES_DIR, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
app.mount("/frames", StaticFiles(directory=OUTPUT_FRAMES_DIR), name="frames")

@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Save file with a unique name
    file_ext = file.filename.split(".")[-1]
    file_id = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Process video and generate summary
    extracted_frames = extract_frames(file_path, OUTPUT_FRAMES_DIR, frame_interval=30)
    
    if not extracted_frames:
        return JSONResponse(content={"error": "No frames extracted from the video"}, status_code=500)

    video_summary = process_video_frames(extracted_frames) or "Summary generation failed."

    base_url = str(request.base_url).rstrip("/")

    return JSONResponse(content={
        "filename": file.filename,
        "file_id": file_id,
        "summary": video_summary,
        "video_url": f"{base_url}/static/{file_id}",
        "frames_url": [f"{base_url}/frames/{os.path.basename(frame)}" for frame in extracted_frames]
    })

@app.get("/")
async def serve_index():
    index_path = "index.html"
    if not os.path.exists(index_path):
        return JSONResponse(content={"error": "index.html not found"}, status_code=404)
    
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html")

@app.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, file_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return JSONResponse(content={"message": "File deleted successfully", "file_id": file_id})
    return JSONResponse(content={"error": "File not found"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
