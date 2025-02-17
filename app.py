from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from api import camera_router, streaming_router, settings_router, logs_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static files config
app.mount("/logs", StaticFiles(directory="logs"), name="logs")
app.mount("/output", StaticFiles(directory="output"), name="output")
app.include_router(camera_router, prefix="/api/cameras")
app.include_router(streaming_router, prefix="/api/streams")

app.include_router(settings_router, prefix="/api/settings")

app.include_router(logs_router, prefix="/api/analytics")
