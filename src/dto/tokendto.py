from datetime import datetime

from pydantic import BaseModel, ConfigDict

class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    token: str


class CreateRefreshTokenDTO(BaseModel):
    token: str
    user_id: int
    expires_at: datetime