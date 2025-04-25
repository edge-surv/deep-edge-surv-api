from fastapi import APIRouter, File, UploadFile, Form
from uuid import uuid4
import os
from fastapi.responses import JSONResponse
from config import ROOT_DIR
from utils.s3 import save_uploaded_file
from test import detect_objects
from models import UploadSearchRequest

search_router = APIRouter()


UPLOAD_DIR = os.path.join(ROOT_DIR, "s3", "videos")


@search_router.post("/upload-search")
async def search_items(
    prompt: str = Form(...),
    confidence: float = Form(0.25),
    save_output: bool = Form(True),
    file: UploadFile = File(...),
):
    """
    Upload a video and search for objects within it using YOLOWorld model.
    """
    if not file or not prompt:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Missing file or prompt",
                "success": False,
            },
        )

    # Generate unique filename and save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"

    try:
        # Save uploaded file locally
        content = await file.read()

        # Save to local storage and get URL
        video_url = save_uploaded_file(content, unique_filename, "videos")

        # Perform detection
        results = detect_objects(
            prompt=prompt, video_path=file_path, confidence=confidence
        )

        # Save detected frames to local storage
        frame_urls = []
        for frame in results["frames"]:
            # Save each frame to local storage with type "frames"
            frame_url = save_uploaded_file(frame["data"], frame["name"], "frames")
            frame_urls.append(frame_url)

        # Clean up temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "original_video_url": video_url,
                "detected_image_urls": frame_urls,
                "total_detections": results["total_detections"],
            },
        )

    except Exception as e:
        if os.path.exists(file_path):
            os.unlink(file_path)

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(e),
            },
        )
