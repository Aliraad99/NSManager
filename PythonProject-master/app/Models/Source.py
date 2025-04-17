from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from app.Models.Stream import Stream

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

   # Stream = relationship("Stream", back_populates="Source")