from pydantic import BaseModel

class LoginModel(BaseModel):
    UserEmail: str
    UserPassword: str