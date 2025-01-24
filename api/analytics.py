from fastapi import APIRouter


analytics_router = APIRouter()


@analytics_router.get("/")
def get_analytics():
    pass