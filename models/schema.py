from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# user model
class UserData(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    password: str


# camera model
class Camera(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    host: str
    port: int
    name: str
    username: str
    password: str
    provider: str


# settings model
class Settings(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    detection_objects: List[str]
    enabled: bool
    minimum_confidence: int | float
    enable_tracking: bool
    enable_counting: bool


class Storage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    camera_id: str
    camera_name: str
    filename: str
    date: str
    time: str


class Logs(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    camera_id: str
    filename: str
    objects_detected: List[str| int]
    date: str
    time: str
