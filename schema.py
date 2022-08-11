from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field


class StudentSchema(BaseModel):
    # Student_id: Optional[int]
    student_name: Optional[str]
    aadhar_number: str

    class Config:
        orm_mode = True


class StudentUpdateSchema(BaseModel):
    student_id: Optional[int]
    student_name: Optional[str]

    class Config:
        orm_mode = True


class SubjectSchema(BaseModel):
    # Student_id: Optional[int]
    subject_name: Optional[str]

    class Config:
        orm_mode = True


class SubjectUpdateSchema(BaseModel):
    subject_id: Optional[int]
    subject_name: Optional[str]

    class Config:
        orm_mode = True


class MarkSchema(BaseModel):
    student_id: int
    subject_id: int
    mark: int

    class Config:
        orm_mode = True


class MarkUpdateSchema(BaseModel):
    mark_id: int
    student_id: int
    subject_id: int
    mark: int

    class Config:
        orm_mode = True


class FetchDetailSchema(BaseModel):
    subject_id: int
    subject_name: str
    mark: int

    class Config:
        orm_mode = True


class FetchAllSchema(BaseModel):
    student_id: int
    student_name: str
    details: List[FetchDetailSchema] = []

    class Config:
        orm_mode = True


class FetchAllStudents(BaseModel):
    students: List[FetchAllSchema] = []

    class Config:
        orm_mode = True
