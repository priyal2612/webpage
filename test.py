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






