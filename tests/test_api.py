import pytest
from fastapi.testclient import TestClient
from app.main import app, ai_client
from app.repository import repo

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    repo.clear()
    ai_client.is_down = False
    yield
    repo.clear()

def test_manual_create():
    res = client.post("/exercises", json={"name": "Присідання", "difficulty": "початковий"})
    assert res.status_code == 201
    assert res.json()["id"] == 1

    list_res = client.get("/exercises")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

def test_manual_create_empty_name():
    res = client.post("/exercises", json={"name": "   "})
    assert res.status_code == 422
    assert len(repo.list_all()) == 0

def test_ai_create_success():
    res = client.post("/exercises/from-text", json={"text": "Звичайні віджимання від підлоги"})
    assert res.status_code == 201
    assert res.json()["name"] == "Віджимання від підлоги"
    assert len(repo.list_all()) == 1

def test_ai_create_no_exercise_name():
    res = client.post("/exercises/from-text", json={"text": "Якась вправа з гантелями"})
    assert res.status_code == 422
    assert "Відсутня назва" in res.json()["detail"]
    assert len(repo.list_all()) == 0

def test_ai_create_hallucinated_equipment():
    res = client.post("/exercises/from-text", json={"text": "Випадання вперед з вагою"})
    assert res.status_code == 422
    assert "не згадується" in res.json()["detail"]
    assert len(repo.list_all()) == 0

def test_ai_outage_fallback():
    ai_client.is_down = True

    res_ai = client.post("/exercises/from-text", json={"text": "Віджимання від підлоги"})
    assert res_ai.status_code == 503

    res_manual = client.post("/exercises", json={"name": "Планка"})
    assert res_manual.status_code == 201
    assert len(repo.list_all()) == 1