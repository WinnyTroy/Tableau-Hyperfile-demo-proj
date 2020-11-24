import sqlalchemy
from .database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    text = Column(String(255), index=True)
    display = Column(Boolean)
