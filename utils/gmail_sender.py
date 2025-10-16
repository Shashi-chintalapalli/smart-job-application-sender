import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_via_gmail(sender_email, app_password, recipient_email, subject, body, resume_file=None):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # ✅ Attach resume exactly as uploaded
    if resume_file is not None:
        resume_file.seek(0)  # Reset pointer to start
        resume_bytes = resume_file.read()
        resume_name = resume_file.name

        part = MIMEApplication(resume_bytes, Name=resume_name)
        part.add_header("Content-Disposition", f'attachment; filename="{resume_name}"')
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)
