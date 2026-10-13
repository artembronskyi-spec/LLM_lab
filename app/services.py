import re
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, status

ALLOWED_DIFFICULTIES = {"початковий", "середній", "високий"}

KNOWN_EXERCISES = {
    "віджимання": ("Віджимання від підлоги", "початковий", "без обладнання"),
    "присідання": ("Присідання зі штангою", "високий", "штанга"),
    "підтягування": ("Підтягування широким хватом", "середній", "турнік"),
    "жим": ("Жим гантелей лежачи", "середній", "гантелі"),
    "планка": ("Планка для пресу", "початковий", "без обладнання"),
    "станова": ("Станова тяга", "високий", "штанга"),
    "випадання": ("Випади вперед", "середній", "гайка"),
    "випади": ("Випади вперед", "середній", "гайка")
}

def parse_text_to_exercise(text: str) -> Dict[str, Any]:
    clean_text = text.lower().strip()

    # Якщо текст абстрактний або без конкретної вправи
    keywords = ["віджимання", "присідання", "підтягування", "жим", "планка", "станова", "випади", "випадання"]
    has_keyword = any(kw in clean_text for kw in keywords)

    if not has_keyword or "якась вправа" in clean_text:
        return {"name": None, "difficulty": "початковий", "equipment": "гантелі"}

    for key, (name, diff, equip) in KNOWN_EXERCISES.items():
        if key in clean_text:
            return {"name": name, "difficulty": diff, "equipment": equip}

    return {"name": None, "difficulty": None, "equipment": None}


def validate_proposal(proposal: Dict[str, Any], raw_text: str) -> Tuple[bool, str]:
    name = proposal.get("name")
    if not name or not str(name).strip():
        return False, "Відсутня назва вправи (потрібне уточнення)"

    difficulty = proposal.get("difficulty")
    if difficulty and difficulty not in ALLOWED_DIFFICULTIES:
        return False, f"Недопустима складність: {difficulty}"

    equipment = proposal.get("equipment")
    if equipment and equipment.lower() not in ["без обладнання", "none", "null"]:
        raw_words = set(re.findall(r'\w+', raw_text.lower()))
        equip_words = set(re.findall(r'\w+', equipment.lower()))

        matches = False
        for eq_word in equip_words:
            if len(eq_word) < 3:
                continue
            if any(eq_word[:3] in rw for rw in raw_words if len(rw) >= 3):
                matches = True
                break

        if not matches:
            return False, f"Обладнання '{equipment}' не згадується в тексті"

    return True, "OK"


class LLMClient:
    def __init__(self):
        self.is_down = False

    def parse(self, text: str) -> Dict[str, Any]:
        if self.is_down:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервіс AI тимчасово недоступний"
            )
        return parse_text_to_exercise(text)