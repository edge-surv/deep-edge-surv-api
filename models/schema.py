from typing import List

from pydantic import BaseModel


# user model
class UserData(BaseModel):
    username: str
    password: str


# camera model
class Camera(BaseModel):
    id: str
    host: str
    port: int
    name: str
    username: str
    password: str
    provider: str


# settings model
class Settings(BaseModel):
    detection_objects: List[str]
    enabled: bool
    minimum_confidence: int
    enable_tracking: bool
    enable_segmentation: bool
    enable_counting: bool
