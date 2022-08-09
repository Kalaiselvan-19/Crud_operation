from fastapi.testclient import TestClient
from app.main import app
from models import Student, Subject, Mark


def test_all_endpoints():
    # note that TestClient is only sync, don't use asyns here
    client = TestClient(app)
    # note that you need to connect to database manually
    # or use client as contextmanager during tests
    with client as client:
        # response = client.post("/add-student", json={"student_name": "kalai"})
        # item = Student(**response.json())
        # assert item.student_id is not None

        response = client.get("/all-student")
        items = [Student(**student_name) for student_name in response.json()]
        assert items[0] == Student.student_id

        items[0].student_name = "New name"
        response = client.put(f"/student/{items[0].student_id}", json=items[0].dict())
        assert response.json() == items[0].dict()

        response = client.get("/all-student")
        items = [Student(**student_name) for student_name in response.json()]
        assert items[0].student_name == "New name"

        response = client.delete(f"/stud-delete/{items[-1].student_id}", json=items[-1].dict())
        assert response.json().get("deleted_rows", "__UNDEFINED__") != "__UNDEFINED__"
        response = client.get(f"/student/{items[-1].student_id}")
        items = response.json()
        print(items)
        assert len(items) == 0
# # For Subject
        # response = client.post("/add-subject", json={"subject_name": "Maths"})
        # item = Subject(**response.json())
        # assert item.subject_id is not None
        #
        # response = client.get("/all-subject")
        # items = [Subject(**subject_name) for subject_name in response.json()]
        # assert items[0] == Subject.subject_id
        #
        # items[0].subject_name = "New Subject"
        # response = client.put(f"/subject/{items[0].subject_id}", json=items[0].dict())
        # assert response.json() == items[0].dict()
        #
        # response = client.get("/all-subject")
        # items = [Subject(**subject_name) for subject_name in response.json()]
        # assert items[0].subject_name == "New Subject"
        # # for mark
        # response = client.post("/add-mark", json={"student_id": 1, "subject_id": 1, "mark": 80})
        # item = Mark(**response.json())
        # assert item.mark_id is not None
        #
        # response = client.get("/all-mark")
        # items = [Mark(**mark) for mark in response.json()]
        # assert items[0] == Mark.mark_id
        #
        # items[0].mark = 100
        # response = client.put(f"/mark/{items[0].mark_id}", json=items[0].dict())
        # assert response.json() == items[0].dict()
        #
        # response = client.get("/all-mark")
        # items = [Mark(**mark) for mark in response.json()]
        # assert items[0].mark == 100
