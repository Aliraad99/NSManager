from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'Users'
    Id = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String)
    MiddleName = Column(String)
    LastName = Column(String)
    Email = Column(String, nullable=False)
    Password = Column(String)
    
    