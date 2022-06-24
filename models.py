from typing import Optional

import ormar
import sqlalchemy

from database import metadata, database, DATABASE_URL
import databases


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Student(ormar.Model):
    class Meta(BaseMeta):
        tablename = "Student"

    student_id: int = ormar.Integer(primary_key=True)
    student_name: str = ormar.String(max_length=100)


class Subject(ormar.Model):
    class Meta(BaseMeta):
        tablename = "Subject"

    subject_id: int = ormar.Integer(primary_key=True)
    subject_name: str = ormar.String(max_length=100)


class Mark(ormar.Model):
    class Meta(BaseMeta):
        tablename = "Mark"

    mark_id: int = ormar.Integer(primary_key=True)
    student_id: int = ormar.ForeignKey(Student, default=None)
    subject_id: int = ormar.ForeignKey(Subject, default=None)
    mark: int = ormar.Integer()


engine = sqlalchemy.create_engine(DATABASE_URL)
# just to be sure we clear the db before
# metadata.create_all(engine)
metadata.create_all(engine)
