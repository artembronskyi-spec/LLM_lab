from typing import Optional, Literal
from pydantic import BaseModel, Field

Difficulty = Literal["початковий", "середній", "високий"]

class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1)
    difficulty: Optional[Difficulty] = None
    equipment: Optional[str] = None

class ExerciseResponse(ExerciseCreate):
    id: int

class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)