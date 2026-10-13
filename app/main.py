from typing import List
from fastapi import FastAPI, HTTPException, status
from app.models import ExerciseCreate, ExerciseResponse, TextRequest
from app.repository import repo
from app.services import LLMClient, validate_proposal

app = FastAPI(title="Exercise Catalog API")
ai_client = LLMClient()

@app.get("/exercises", response_model=List[ExerciseResponse])
def get_exercises():
    return repo.list_all()

@app.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(data: ExerciseCreate):
    if not data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Назва вправи не може бути порожньою"
        )
    return repo.add(data)

@app.post("/exercises/from-text", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_from_text(payload: TextRequest):
    proposal = ai_client.parse(payload.text)

    valid, reason = validate_proposal(proposal, payload.text)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=reason
        )

    item = ExerciseCreate(
        name=proposal["name"],
        difficulty=proposal.get("difficulty"),
        equipment=proposal.get("equipment")
    )
    return repo.add(item)

@app.post("/debug/toggle-outage")
def toggle_outage():
    ai_client.is_down = not ai_client.is_down
    return {"is_down": ai_client.is_down}
