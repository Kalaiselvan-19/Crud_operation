import app
import crud


def test_read_note(test_app, monkeypatch):
    test_data = {"id": 1, "student_id": 1, "student_name": "something else"}

    async def mock_get(student_id=int):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("student/1")
    assert response.status_code == 200
    assert response.json() == test_data
