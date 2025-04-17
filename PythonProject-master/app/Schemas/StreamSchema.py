from pydantic import BaseModel
from fastapi import Body

class StreamSchema(BaseModel):
    id : int
    sourceID : int
    stream_name : str
    stream_url : str

    class Config:
        from_attributes = True

