from pydantic import BaseModel, EmailStr, Field


class SUser(BaseModel):
    id: int
    name: str
    email: EmailStr = Field(..., description="Email")


class SUserRegister(BaseModel):
    name: str
    email: EmailStr = Field(..., description="Email")
    password: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Password must be at least 5 characters long",
    )


class SUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Password must be at least 5 characters long",
    )
