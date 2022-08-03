import models
import schema


async def post(student: schema.StudentSchema):
    student = models.Student(student_name=student.student_name)
    response = await student.save()
    return response


async def get(student_id: int):
    student = await models.Student.objects.get(student_id=student_id)
    return student


async def all_student():
    student = await models.Student.objects.all()
    return student
