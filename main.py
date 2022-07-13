from email.mime.application import MIMEApplication

from fastapi import FastAPI, BackgroundTasks
from fpdf import FPDF, HTMLMixin
from generatexl import Writter
import models
import schema
from database import database
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
async def fetch_one_detail_pdf(student_id: int):
    Final_res = None
    students_db = await models.Student.objects.get(student_id=student_id)
    mark = await models.Mark.objects.filter(student_id=student_id).all()
    sub = 1
    res = []

    class WriteHtmlPDF(FPDF, HTMLMixin):
        pass

    html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <h2 align="center">Report Card</h2>
            </head>"""

    html += f"""<body>
                <h3 align="center"> Name of the Student:{students_db.student_name}    ID:{students_db.student_id}</h3>
                <table class = "class" width="60%" height="100% align="center" border = "1">
                  <thead>
                    <tr text-align = "center">
                      <th align="center" width="30%"> S.No</th>
                      <th align="center" width="40%">Subject Name</th>
                      <th align="center" width="30%">Mark</th>
                      <th align="center" width="30%">Result</th>
                    </tr>
                  </thead>
                  <tbody class= "text-center text-sm">"""
    total_marks = 0
    for i in mark:
        total_marks += i.mark
        sub_id = i.subject_id.subject_id
        sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()
        if i.mark >= 35:
            result = "PASS"
            res.append(result)
        else:
            result = "FAIL"
            res.append(result)
        html += "<tr>"
        html += """<td  align="center"  border = "1">""" + str(sub) + "</td>"
        html += """<td  align="center"  border = "1">""" + sub_name.subject_name + "</td>"
        html += """<td  align="center"  border = "1">""" + str(i.mark) + "</td>"
        if result == "PASS":
            html += """<td  align="center"  border = "1">""" + result + "</td>"
        else:
            html += """<td  align="center"  border = "1"><font color="#FF0000">""" + result + "</font></td>"
        html += "</tr>"
        sub += 1
    for i in res:
        if i == "FAIL":
            Final_res = "FAIL"
            break
        else:
            Final_res = "PASS"
    if Final_res == "FAIL":
        html += f"""</tbody>
                <tbody width="2%">
                    <tr text-align = "center">
                      <td align="left" width="70%" ><font color="#FF0000"><B>Result: {Final_res}</font></B></td>
                      <td align="left" width="60%" ><font color="#000000" ><B>Total Marks: {total_marks}</font></B></td>
                    </tr>
                  </tbody>
              </table>
            </body></html>"""
    else:
        html += f"""</tbody>
                        <tbody width="2%">
                            <tr text-align = "center">
                              <td align="left" width="70%"><B>Result: {Final_res}</B></td>
                              <td align="left" width="60%" ><B>Total Marks: {total_marks}</B></td>
                            </tr>
                          </tbody>
                      </table>
                    </body></html>"""

    pdf = WriteHtmlPDF()
    # First page
    pdf.add_page()
    pdf.write_html(html)
    pdf.output(f"{students_db.student_name}.pdf")
    return f" home/kalaiselvan/PycharmProjects/Curd_operation/{students_db.student_name}.pdf"


@app.get("/fetch-one-detail-in-csv")
async def fetch_one_detail_csv(student_id: int):
    Final_res = None
    stud = await models.Student.objects.get(student_id=student_id)
    mark = await models.Mark.objects.filter(student_id=student_id).all()
    writer = Writter()
    writer.create(f"{stud.student_name}.xlsx")
    row = 0
    col = 0
    writer.write(row, col, "S.NO")
    writer.write(row, col + 1, "Subject_name")
    writer.write(row, col + 2, "Mark")
    writer.write(row, col + 3, "Result")
    res = []
    total_marks = 0
    SNO = 1
    for i in mark:
        total_marks += i.mark
        sub_id = i.subject_id.subject_id
        sub_name = await models.Subject.objects.filter(subject_id=sub_id).get()
        if i.mark >= 35:
            result = "PASS"
            res.append(result)
        else:
            result = "FAIL"
            res.append(result)
        writer.write(row + 1, col, SNO)
        writer.write(row + 1, col + 1, sub_name.subject_name)
        writer.write(row + 1, col + 2, i.mark)
        writer.write(row + 1, col + 3, result)
        row += 1
        SNO += 1
    for i in res:
        if i == "FAIL":
            Final_res = "FAIL"
            break
        else:
            Final_res = "PASS"
    writer.write(row + 2, col, f"Result:{Final_res}")
    writer.write(row + 2, col + 2, f"Total_Mark:{total_marks}")

    writer.close()
    return f" home/kalaiselvan/PycharmProjects/Curd_operation/{stud.student_name}.xlsx"


@app.get('/Mail/Pdf')
async def send_mail(student_id: int):
    stud = await models.Student.objects.get(student_id=student_id)
    await fetch_one_detail_pdf(student_id=student_id)
    mail_content = f'The Mark statement for the  {stud.student_name}'
    # The mail addresses and password
    sender_address = 'kalaiselvan1360@gmail.com'
    sender_pass = 'rmhmqwftwohgaitx'
    receiver_address = 'kalaiselva1901@gmail.com'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Student_Detail'
    # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content))
    attach_file_name = f'{stud.student_name}.pdf'
    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    attach = MIMEBase('application', 'octate-stream')
    attach.set_payload(attach_file.read())
    encoders.encode_base64(attach)  # encode the attachment

    with open(f"/home/kalaiselvan/PycharmProjects/Crud_operation/{stud.student_name}.pdf", "rb") as f:
        attach = MIMEApplication(f.read(), _subtype='pdf')
        # addattach header with filename
        # attach.add_header('Content-Decomposition', 'attachment',
        #                   filename=str(f"/home/kalaiselvan/PycharmProjects/Crud_operation/{stud.student_name}.pdf"))
        attach.add_header('Content-Disposition', 'attachment; filename="%s"' % attach_file_name)

        message.attach(attach)
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)

    session.quit()
    return "Mail sended Sucessfully"


@app.get('/Mail/csv')
async def send_mail_csv(student_id: int):
    stud = await models.Student.objects.get(student_id=student_id)
    await fetch_one_detail_csv(student_id=student_id)
    mail_content = f'The Mark statement for the  {stud.student_name}'
    # The mail addresses and password
    sender_address = 'kalaiselvan1360@gmail.com'
    sender_pass = 'rmhmqwftwohgaitx'
    receiver_address = 'kalaiselva1901@gmail.com'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Student_Detail'
    # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content))
    attach_file_name = f'{stud.student_name}.xlsx'
    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    attach = MIMEBase('application', 'octate-stream')
    attach.set_payload(attach_file.read())
    encoders.encode_base64(attach)  # encode the attachment
    with open(f"/home/kalaiselvan/PycharmProjects/Crud_operation/{stud.student_name}.xlsx", "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="vnd.openxmlformats.officedocument.spreadsheetml.sheet")
        attach.add_header('Content-Disposition', 'attachment; filename="%s"' % attach_file_name)
        message.attach(attach)
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)

    session.quit()
    return "Mail sended Sucessfully"
