from pydantic import BaseModel, Field, field_validator

from typing import Optional, Dict, Any


class Credentials(BaseModel):
    email: str = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user")

    @field_validator("email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Email must be a valid email address")
        return v

    @field_validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ResponseModel(BaseModel):
    status: str = Field(..., description="The status of the response")
    message: str = Field(..., description="The message of the response")
    data: Optional[Dict[str, Any]] = Field(None, description="The data of the response")


class TaskResponse(BaseModel):
    message: str = Field(..., description="The message of the response")
    sync_task_id: str = Field(..., description="The sync task ID of the response")
    finished: bool = Field(..., description="The finished status of the response")


class TaskStatus(BaseModel):
    task_id: str = Field(..., description="The task ID of the response")
    status: str = Field(..., description="The status of the response")
    result: Optional[Any] = Field(None, description="The result of the response")
