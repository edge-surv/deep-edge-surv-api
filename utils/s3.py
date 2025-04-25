import os
from config import ROOT_DIR
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

# Define storage directories
S3_DIR = os.path.join(ROOT_DIR, "s3")
VIDEOS_DIR = os.path.join(S3_DIR, "videos")
FRAMES_DIR = os.path.join(S3_DIR, "frames")


def init_storage(app: FastAPI):
    """Initialize storage directories and mount static file serving"""
    # Create directories if they don't exist
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # Mount S3 directory for static file serving
    app.mount("/s3", StaticFiles(directory=S3_DIR), name="s3")


def save_uploaded_file(file_content: bytes, filename: str, file_type: str = "videos"):
    """
    Save uploaded file to appropriate directory and return its URL path
    """
    if file_type not in ["videos", "frames"]:
        return None

    directory = VIDEOS_DIR if file_type == "videos" else FRAMES_DIR
    file_path = os.path.join(directory, filename)

    # Save the file
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Return the URL path
    return f"/s3/{file_type}/{filename}"


def get_file_url(filename: str, file_type: str = "videos"):
    """Generate URL for accessing stored files"""
    return f"/s3/{file_type}/{filename}"


def delete_file(filename: str, file_type: str = "videos") -> bool:
    """Delete file from storage"""
    if file_type not in ["videos", "frames"]:
        raise ValueError("file_type must be either 'videos' or 'frames'")

    directory = VIDEOS_DIR if file_type == "videos" else FRAMES_DIR
    file_path = os.path.join(directory, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
