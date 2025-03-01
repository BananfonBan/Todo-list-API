from pydantic import BaseModel

class SJWTToken(BaseModel):
    access_token: str
    refresh_token: str | None
