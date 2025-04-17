from pydantic import BaseModel
from fastapi import Body

class UserSchema(BaseModel):
    Id : int
    FirstName : str
    MiddleName : str
    LastName : str
    Email: str
    Password: str
    
    class Config:
        from_attributes = True
