
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String

class Stream(Base):
    __tablename__ = 'streams'
    id = Column(Integer, primary_key=True, index=True)
    sourceID = Column(Integer, ForeignKey("sources.id"))
    stream_name = Column(String)
    stream_url = Column(String)
    
    #Source = relationship("Source", back_populates="Streams")
