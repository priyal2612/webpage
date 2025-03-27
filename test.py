import cv2
import os

def extract_frames(video_path, output_folder, frame_interval=1):
    """
    Extracts frames from a video and saves them as images.

    :param video_path: Path to the input video file.
    :param output_folder: Folder where extracted images will be saved.
    :param frame_interval: Extract every Nth frame (default: 1 - every frame).
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Stop if video ends

        # Save every Nth frame
        if frame_count % frame_interval == 0:
            img_filename = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(img_filename, frame)
            print(f"Saved {img_filename}")
            saved_count += 1

        frame_count += 1

    cap.release()
    print("Frame extraction completed.")

# Example usage
video_path = "C:\\Users\\hp\\Downloads\\IMG_2491 2.MOV"  # Change this to your video file path
output_folder = "output_frames"  # Folder to save images
frame_interval = 30  # Extract every 30th frame (adjust as needed)   (video length = 30 sec, image_frame = 60 at interval of 30)

extract_frames(video_path, output_folder, frame_interval)






#amazonnova.py

import os
import cv2
import json
import boto3
import re
import base64
from datetime import datetime
from boto3.dynamodb.conditions import Key

system_prompt =  """You are an expert video analysis assistant. Your task is to analyze multiple consecutive video frames, 
recognize objects, human actions, and environmental details, and provide structured insights. Ensure consistency across frames
 and highlight any notable changes or events. The summary should be clear, concise, and formatted in JSON."""
runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
prompt=[]

def extract_frames(video_path, output_folder, frame_interval=1):
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return []

    frame_count = 0
    saved_images = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Stop if video ends

        if frame_count % frame_interval == 0:
            img_filename = os.path.join(output_folder, f"frame_{len(saved_images):04d}.jpg")
            cv2.imwrite(img_filename, frame)
            saved_images.append(img_filename)
            print(f"Saved {img_filename}")

        frame_count += 1

    cap.release()
    print("✅ Frame extraction completed.")
    return saved_images

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

def claude_prompt_image(prompt, file_base64):
    payload = {
        "system": [{"text": system_prompt}],
        "messages": [{"role": "user", "content": []}],
    }

    for i, file in enumerate(file_base64):
        if file is not None:  # Check if the image was converted successfully
            payload["messages"][0]["content"].append({"image":
                                                      {"format": "jpeg", 
                                                       "source": {"bytes": file}
                                                       }
                                                    })
            payload["messages"][0]["content"].append({"text": f"Image {i}:"})

    payload["messages"][0]["content"].append({"text": prompt})

    try:
        model_response = runtime.invoke_model(
            modelId="us.amazon.nova-lite-v1:0",
            body=json.dumps(payload)
        )
        dict_response_body = json.loads(model_response.get("body").read())
        return dict_response_body
    except Exception as e:
        print(f"Error invoking model: {e}")
        return None

def process_video_frames(frames):
    batch_size = 5
    summary = []

    for i in range(0, len(frames), batch_size):
        batch_files = frames[i:i + batch_size]
        file_base64 = [image_to_base64(img) for img in batch_files]

        print(f"Processing batch {i // batch_size + 1}: {batch_files}")

        prompt="""Analyze these five consecutive video frames and provide a structured summary.Identify key objects, 
        human actions, and any significant events or changes observed between frames. Output the response in JSON format:
        {  
        'summary': 'A brief description of the scene and any changes.',  
        'objects': ['List of detected objects, e.g., person, chair, screen'],  
        'actions': ['List of actions occurring, e.g., walking, sitting, talking'],  
        'notable_changes': 'Describe any movement, new objects appearing/disappearing, or major alterations in the scene.'  
        }  
        Ensure accuracy and consistency across frames."""

        model_response = claude_prompt_image(prompt, file_base64)
        
        if model_response is not None:
            try:
                raw_text = model_response["output"]["message"]["content"][0]["text"].replace('\n', '').replace('\\"', '"')
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if match:
                    raw_text = match.group(0)
                response_dict = json.loads(raw_text)
                summary.append(response_dict)
            except Exception as e:
                print("llm_resposne:", raw_text)
                print("Unexpected error:", str(e))

    return summary


if __name__ == "__main__":
    video_path = "C:\\Users\\hp\\OneDrive\\Desktop\\photos iphone\\manali\\IMG_0138.MOV"  # Change this to your video file path
    output_folder = "output_frames"
    frame_interval = 30  # Extract every 30th frame

    start_time = datetime.now()
    
    extracted_frames = extract_frames(video_path, output_folder, frame_interval)

    if extracted_frames:
        video_summary = process_video_frames(extracted_frames)
        print("\n🔹 Final Video Summary:")
        for idx, scene in enumerate(video_summary, 1):
            print(f"\nScene {idx}: {scene}")

    print("\n⏳ Total Time Taken:", datetime.now() - start_time) 




    #index.html
    <!-- <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Image Upload</title>
</head>
<body>
    <h2>Upload Image</h2>
    <input type="file" id="fileInput">
    <button onclick="uploadFile()">Upload</button>
    
    <h2>Uploaded Images</h2>
    <div id="imageContainer"></div>

    <script>
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];

            if (!file) {
                alert("Please select a file.");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://localhost:8000/upload/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                displayImage(data);
            } else {
                alert("Upload failed!");
            }
        }

        function displayImage(data) {
            const imageContainer = document.getElementById('imageContainer');

            const div = document.createElement('div');
            div.id = `image-${data.file_id}`;
            div.innerHTML = `
                <img src="${data.url}" alt="${data.filename}" width="200"><br>
                <pre>${JSON.stringify(data, null, 2)}</pre>
                <button onclick="deleteFile('${data.file_id}')">Delete</button>
                <hr>
            `;
            imageContainer.appendChild(div);
        }

        async function deleteFile(fileId) {
            const response = await fetch(`http://localhost:8000/delete/${fileId}`, {
                method: "DELETE"
            });

            const data = await response.json();
            if (response.ok) {
                document.getElementById(`image-${fileId}`).remove();
                alert("File deleted successfully.");
            } else {
                alert("Failed to delete file.");
            }
        }
    </script>
</body>
</html> -->




<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Image Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            text-align: center;
        }
        header {
            background: #007BFF;
            color: white;
            padding: 15px;
            font-size: 24px;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        input[type="file"] {
            margin-top: 10px;
        }
        button {
            margin-top: 10px;
            background: #007BFF;
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 5px;
            transition: 0.3s;
        }
        button:hover {
            background: #0056b3;
        }
        #imageContainer {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }
        .image-card {
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            width: 220px;
        }
        .image-card img {
            width: 100%;
            border-radius: 5px;
        }
        footer {
            margin-top: 30px;
            padding: 10px;
            background: #007BFF;
            color: white;
        }
    </style>
</head>
<body>
    <header>Aeyi Model Demo</header>
    
    <div class="container">
        <h2>Upload Image</h2>
        <input type="file" id="fileInput">
        <button onclick="uploadFile()">Upload</button>
    </div>
    
    <h2>Uploaded Images</h2>
    <div id="imageContainer"></div>
    
    <footer>Aeyi Model Demo &copy; 2025</footer>

    <script>
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];

            if (!file) {
                alert("Please select a file.");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://localhost:8000/upload/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                displayImage(data);
            } else {
                alert("Upload failed!");
            }
        }

        function displayImage(data) {
            const imageContainer = document.getElementById('imageContainer');
            
            const div = document.createElement('div');
            div.className = "image-card";
            div.id = `image-${data.file_id}`;
            div.innerHTML = `
                <img src="${data.url}" alt="${data.filename}"><br>
                <pre>${JSON.stringify(data, null, 2)}</pre>
                <button onclick="deleteFile('${data.file_id}')">Delete</button>
            `;
            imageContainer.appendChild(div);
        }

        async function deleteFile(fileId) {
            const response = await fetch(`http://localhost:8000/delete/${fileId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                document.getElementById(`image-${fileId}`).remove();
                alert("File deleted successfully.");
            } else {
                alert("Failed to delete file.");
            }
        }
    </script>
</body>
</html>




#main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from PIL import Image
import io
import uuid
import os
import uvicorn
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
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Save file with unique name
    file_ext = file.filename.split(".")[-1]
    file_id = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    # Dummy Processing (you can replace this with your ML model or any logic)
    image = Image.open(file_path)
    width, height = image.size
    
    return JSONResponse(content={
        "filename": file.filename,
        "file_id": file_id,
        "url": f"http://localhost:8000/static/{file_id}",
        "width": width,
        "height": height
    })

# Serve uploaded files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

@app.get("/")
async def serve_index():
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, media_type="text/html")


@app.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, file_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return JSONResponse(content={"message": "File deleted successfully", "file_id": file_id})
    return JSONResponse(content={"error": "File not found"}, status_code=404)




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)