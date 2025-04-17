from pydantic import BaseModel
from fastapi import Body
 


class SourceSchema(BaseModel):
            id : int
            name : str
       

            class Config:
                from_attributes = True






