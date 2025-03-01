from pydantic import BaseModel, EmailStr


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mod = True
        from_attributes = True


class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        orm_mod = True
        from_attributes = True


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mod = True
        from_attributes = True

