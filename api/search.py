from fastapi import APIRouter, UploadFile, File
from uuid import uuid4
import os
from config import ROOT_DIR
from fastapi.responses import JSONResponse

from agents.tasks import search_video

search_router = APIRouter()


UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")


@search_router.post("/")
async def search_items(
    file: UploadFile = File(...),
    prompt: str = None,
    confidence: float = 0.25,
    save_output: bool = True,
):
    """
    Upload a video and search for objects within it using YOLOWorld model.

    Args:
        file: The video file to analyze
        prompt: What to search for (e.g., "person wearing red", "blue car")
        confidence: Detection confidence threshold
        save_output: Whether to save the annotated video
    """
    if not file:
        return JSONResponse(
            status_code=400,
            content={
                "message": "No file uploaded",
                "file": False,
            },
        )

    if not prompt:
        return JSONResponse(
            status_code=400,
            content={
                "message": "No search prompt provided",
                "prompt": False,
            },
        )

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"

    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:

        return JSONResponse(
            status_code=500, content={"message": f"Failed to save file: {str(e)}", }
        )

    # Perform search
    try:
        results = search_video(
            prompt=prompt,
            source_video=str(file_path),
            confidence=confidence,
            save_output=save_output,
        )

        # Check if search was successful
        if results["search"] == False:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Search failed",
                    "search": False,
                },
            )

        # Construct response
        response = {
            "search": True,
        }
        response["timestamps"] = results["timestamps"]
        response["total_detections"] = results["total_detections"]
        response["output_files"] = results["output_files"]

        return JSONResponse(
            status_code=200,
            content=response,
        )

    except Exception as e:

        print(e)
        # Clean up uploaded file if search fails
        os.unlink(file_path)

        return JSONResponse(
            status_code=400,
            content={
                "search": False,
            },
        )
