from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


# Base Entity
class UserBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the user",
        alias="_id",
    )
    phone: str = Field(..., description="The phone number of the user")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user")
    complete: bool = Field(
        default=False, description="Indicates if the user profile is complete"
    )
    cpf: Optional[str] = Field(None, description="The CPF of the user")
    cnpj: Optional[str] = Field(None, description="The CNPJ of the user")
    created_at: datetime = Field(
        ..., description="The timestamp when the user was created"
    )
    updated_at: datetime = Field(
        ..., description="The timestamp when the user was last updated"
    )

    class Config:
        from_attributes = True
        populate_by_name = True

    @property
    def is_complete(self) -> None:
        if self.name and self.email and self.phone and (self.cpf or self.cnpj):
            self.complete = True
        self.complete


# Data Transfer Objects
class UserCreate(BaseModel):
    phone: str = Field(..., description="The phone number of the user")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user")
    cpf: Optional[str] = Field(None, description="The CPF of the user")
    cnpj: Optional[str] = Field(None, description="The CNPJ of the user")

    @field_validator("phone")
    def phone_must_be_valid(cls, v):
        if len(v) != 11:
            raise ValueError("Phone must be 11 digits")
        return v

    @field_validator("email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Email must be a valid email address")
        return v

    @field_validator("cpf")
    def cpf_must_be_valid(cls, v):
        if len(v) != 11:
            raise ValueError("CPF must be 11 digits")
        return v

    @field_validator("cnpj")
    def cnpj_must_be_valid(cls, v):
        if len(v) != 14:
            raise ValueError("CNPJ must be 14 digits")
        return v

    @field_validator("cpf", "cnpj")
    def cpf_cnpj_must_be_valid(cls, v):
        if v and len(v) != 11 and len(v) != 14:
            raise ValueError("The user must have a valid CPF or CNPJ")
        return v

    @field_validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    phone: Optional[str] = Field(None, description="The phone number of the user")
    name: Optional[str] = Field(None, description="The name of the user")
    email: Optional[str] = Field(None, description="The email address of the user")
    password: Optional[str] = Field(None, description="The password of the user")
    cpf: Optional[str] = Field(None, description="The CPF of the user")
    cnpj: Optional[str] = Field(None, description="The CNPJ of the user")

    @field_validator("phone")
    def phone_must_be_valid(cls, v):
        if v is None:
            return v
        if len(v) != 11:
            raise ValueError("Phone must be 11 digits")
        return v

    @field_validator("email")
    def email_must_be_valid(cls, v):
        if v is None:
            return v
        if "@" not in v:
            raise ValueError("Email must be a valid email address")
        return v

    @field_validator("password")
    def password_must_be_strong(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("cpf")
    def cpf_must_be_valid(cls, v):
        if v is None:
            return v
        if len(v) != 11:
            raise ValueError("CPF must be 11 digits")
        return v

    @field_validator("cnpj")
    def cnpj_must_be_valid(cls, v):
        if v is None:
            return v
        if len(v) != 14:
            raise ValueError("CNPJ must be 14 digits")
        return v
