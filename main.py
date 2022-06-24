from fastapi import FastAPI
from fpdf import FPDF

import models
import schema
from database import database

app = FastAPI()

app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


# create student
@app.post('/add-student')
async def add_student(student: schema.StudentSchema):
    student = models.Student(student_name=student.student_name)
    response = await student.save()
    return response


# create subject
@app.post('/add-subject')
async def add_subject(subject: schema.SubjectSchema):
    subject = models.Subject(subject_name=subject.subject_name)
    response = await subject.save()
    return response


# Create Mark
@app.post('/add-mark')
async def add_mark(mark: schema.MarkSchema):
    mark = models.Mark(student_id=mark.student_id, subject_id=mark.subject_id, mark=mark.mark)
    response = await mark.save()
    return response


# Get all student
@app.get('/all-student')
async def all_student():
    student = await models.Student.objects.all()
    return student


# Get all subject
@app.get('/all-subject')
async def all_subject():
    subject = await models.Subject.objects.all()
    return subject


# Get all mark
@app.get('/all-mark')
async def all_mark():
    mark = await models.Mark.objects.all()
    return mark


# Get one student
@app.get('/student/{student_id}')
async def get_student(student_id: int):
    student = await models.Student.objects.get(student_id=student_id)
    return student


# Get one Subject
@app.get('/subject/{subject_id}')
async def get_subject(subject_id: int):
    subject = await models.Subject.objects.get(subject_id=subject_id)
    return subject


# Get one Mark
@app.get('/mark/{mark_id}')
async def get_mark(mark_id: int):
    mark = await models.Mark.objects.get(mark_id=mark_id)
    return mark


# Update student
@app.put('/student/{student_id}')
async def update_student(student_id: int, student: schema.StudentUpdateSchema):
    stud_update = await models.Student.objects.get(student_id=student_id)
    stud_update.student_name = student.student_name
    stud_update.student_id = student.student_id
    response = await stud_update.update()
    return response


# update subject
@app.put('/subject/{subject_id}')
async def update_subject(subject_id: int, subject: schema.SubjectUpdateSchema):
    sub_update = await models.Subject.objects.get(subject_id=subject_id)
    sub_update.subject_name = subject.subject_name
    sub_update.subject_id = subject.subject_id
    response = await sub_update.update()
    return response


# Update Mark
@app.put('/Mark/{mark_id}')
async def update_mark(mark_id: int, mark: schema.MarkUpdateSchema):
    mark_update = await models.Mark.objects.get(mark_id=mark_id)
    mark_update.mark_id = mark.mark_id
    mark_update.student_id = mark.student_id
    mark_update.subject_id = mark.subject_id
    mark_update.mark = mark.mark
    response = await mark_update.update()
    return response


# Delete student
@app.delete('/delete/{student_id}')
async def delete_student(student: int):
    stud = await models.Student.objects.get(student_id=student)
    await stud.marks.clear(keep_reversed=False)
    await stud.delete()


# Delete subject
@app.delete('/delete/{subject_id}')
async def delete_subject(subject_id: int):
    sub = await models.Subject.objects.get(subject_id=subject_id)
    await sub.marks.clear(keep_reversed=False)
    await sub.delete()


# Delete Mark
@app.delete('/delete/{mark_id}')
async def delete_mark(mark_id: int):
    mark = await models.Mark.objects.get(mark_id=mark_id)
    await mark.delete()


@app.get("/fetch/{student_id}")
async def fetch_mark(student_id: int):
    stud = await models.Student.objects.get(student_id=student_id)
    mark = await models.Mark.objects.filter(student_id=student_id).all()

    details = []
    for i in mark:
        sub_id = i.subject_id.subject_id
        sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()

        s = schema.FetchDetailSchema(
            subject_id=i.subject_id.subject_id,
            subject_name=sub_name.subject_name,
            mark=i.mark
        )
        details.append(s)

    response = schema.FetchAllSchema(
        student_id=stud.student_id,
        student_name=stud.student_name,
        details=details
    )
    return response


@app.get("/fetch_all")
async def fetch_all_mark():
    students_db = await models.Student.objects.all()
    students_list = []

    for students in students_db:
        mark = await models.Mark.objects.filter(student_id=students.student_id).all()
        details = []
        for i in mark:
            sub_id = i.subject_id.subject_id
            sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()

            s = schema.FetchDetailSchema(
                subject_id=i.subject_id.subject_id,
                subject_name=sub_name.subject_name,
                mark=i.mark
            )
            details.append(s)
        response = schema.FetchAllSchema(
            student_id=students.student_id,
            student_name=students.student_name,
            details=details
        )
        students_list.append(response)

    return schema.FetchAllStudents(students=students_list)


# Create pdf for one student
@app.get("/fetch-one-detail-in-pdf")
async def fetch_all_mark_pdf(student_id: int):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=16)

    count = 1

    students_db = await models.Student.objects.get(student_id=student_id)
    mark = await models.Mark.objects.filter(student_id=student_id).all()

    pdf.cell(200, 10, txt=f"{count}. Student name : {students_db.student_name}", ln=1, align='L')
    sub = 1
    for i in mark:
        sub_id = i.subject_id.subject_id
        sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()
        pdf.cell(200, 10, txt=f"  {sub}.Subject name : {sub_name.subject_name}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"    Subject mark : {i.mark}", ln=1, align='L')
        sub += 1
        pdf.cell(200, 10, txt="", ln=1, align='L')
        count += 1

    pdf.output(f"{students_db.student_id}_{students_db.student_name}.pdf")
    return f'/home/kalaiselvan/PycharmProjects/Curd_operation/{students_db.student_id}-{students_db.student_name}.pdf '


# Create pdf file for all data
@app.get("/fetch-all-in-pdf")
async def fetch_all_mark_pdf():
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=16)

    count = 1

    students_db = await models.Student.objects.all()

    for students in students_db:
        mark = await models.Mark.objects.filter(student_id=students.student_id).all()
        pdf.cell(200, 10, txt=f"{count}. Student name : {students.student_name}", ln=1, align='L')
        sub = 1
        for i in mark:
            sub_id = i.subject_id.subject_id
            sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()
            pdf.cell(200, 10, txt=f"  {sub}.Subject name : {sub_name.subject_name}", ln=1, align='L')
            pdf.cell(200, 10, txt=f"    Subject mark : {i.mark}", ln=1, align='L')
            sub += 1
        pdf.cell(200, 10, txt="", ln=1, align='L')
        count += 1

    pdf.output("All_details.pdf")
    return f'/home/kalaiselvan/PycharmProjects/Curd_operation/All_details.pdf '
