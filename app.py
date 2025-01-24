from fastapi import FastAPI
from api import camera_router, streaming_router, settings_router, analytics_router

app = FastAPI()

app.include_router(camera_router, prefix="/api/cameras")
app.include_router(streaming_router, prefix="/api/streams")

app.include_router(settings_router, prefix="/api/settings")

app.include_router(analytics_router, prefix="/api/analytics")
