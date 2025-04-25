from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from utils.s3 import init_storage
from api.search import search_router


app = FastAPI()


# Include routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# # static files config
init_storage(app)
# app.include_router(camera_router, prefix="/api/cameras")
# app.include_router(streaming_router, prefix="/api/streams")
# app.include_router(agents_router, prefix="/api/agents")
# app.include_router(auth_router, prefix="/api/auth/users")
# app.include_router(logs_router, prefix="/api/logs")
app.include_router(search_router, prefix="/api/search")
# app.include_router(notifications_router, prefix="/api/notifications")
