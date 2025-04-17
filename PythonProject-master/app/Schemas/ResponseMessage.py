from pydantic import BaseModel

class ResponseMessage(BaseModel):
    Success: bool
    Message: str