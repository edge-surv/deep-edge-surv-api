import os

from fastapi import APIRouter, status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

from db import storage_table

storage_router = APIRouter()


@storage_router.get('/videos')
def get_storage_videos():
    videos = storage_table.all()

    if len(videos) < 1:
        response = {
            "videos": []
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)

    else:
        response = {
            "videos": videos
        }

        return JSONResponse(response, status_code=status.HTTP_200_OK)


# get the file name
@storage_router.get("/video/{filename}")
async def get_video(filename: str, request: Request):
    file_path = os.path.join("output", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Get the file size
    file_size = os.path.getsize(file_path)

    # Check if the request includes a Range header
    range_header = request.headers.get("Range")
    if range_header:
        # Parse the range header (e.g., "bytes=0-999")
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1

        # Ensure the range is valid
        if start >= file_size or end >= file_size:
            return Response(
                status_code=416,  # Range Not Satisfiable
                headers={
                    "Content-Range": f"bytes */{file_size}"
                }
            )

        # Calculate the content length for the partial response
        content_length = end - start + 1

        # Open the file and seek to the start position
        with open(file_path, "rb") as file:
            file.seek(start)
            data = file.read(content_length)

        # Return a partial content response with headers
        return Response(
            content=data,
            status_code=206,  # Partial Content
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(content_length),
                "Content-Type": "video/mp4",
            }
        )
    else:
        # Serve the full file without additional headers
        return FileResponse(
            file_path,
            media_type="video/mp4",
        )
