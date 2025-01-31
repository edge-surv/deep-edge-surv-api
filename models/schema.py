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
    minimum_confidence: int | float
    enable_tracking: bool
    enable_counting: bool


class Storage(BaseModel):
    id: str
    camera_id: str
    camera_name: str
    filename: str
    date: str
    time: str


class Logs(BaseModel):
    id: str
    camera_id: str
    filename: str
    objects: List[str| int]
    date: str
    time: str
