from datetime import date
from pydantic import BaseModel


class Notes(BaseModel):
    id: int
    username: str
    text: str
    display: bool

    class Config:
        orm_mode = True