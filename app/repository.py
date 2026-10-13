from typing import List
from app.models import ExerciseCreate, ExerciseResponse

class ExerciseRepository:
    def __init__(self):
        self.data: List[ExerciseResponse] = []
        self._id_counter = 1

    def list_all(self) -> List[ExerciseResponse]:
        return self.data

    def add(self, item: ExerciseCreate) -> ExerciseResponse:
        record = ExerciseResponse(
            id=self._id_counter,
            name=item.name.strip(),
            difficulty=item.difficulty,
            equipment=item.equipment.strip() if item.equipment else None
        )
        self.data.append(record)
        self._id_counter += 1
        return record

    def clear(self):
        self.data.clear()
        self._id_counter = 1

repo = ExerciseRepository()