from pydantic import BaseModel, EmailStr, ConfigDict


class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class UserCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    password: str


class UserLoginDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str
