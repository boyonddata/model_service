from typing import Optional
from pydantic import BaseModel, constr


class TextRequest(BaseModel):
    session_id: Optional[int] = None
    message: constr(max_length=100000) 
    #max_length: int = 0

# class TextRequest(BaseModel):
#     session_id: int | None = None
#     message: str