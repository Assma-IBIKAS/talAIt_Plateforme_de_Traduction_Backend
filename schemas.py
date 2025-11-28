from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TranslateRequest(BaseModel):
    text: str
    direction: str  # "fr-en" or "en-fr"

class TranslateResponse(BaseModel):
    translation: str