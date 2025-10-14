import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_via_gmail(sender_email, app_password, recipient_email, subject, body, resume_file=None):
    """
    Sends an email using Gmail SMTP with an optional resume attachment.

    Args:
        sender_email (str): Your Gmail address.
        app_password (str): Your Gmail app password.
        recipient_email (str): HR or recipient email.
        subject (str): Email subject line.
        body (str): Plain text email body.
        resume_file (UploadedFile): Streamlit uploaded resume file.

    Returns:
        True if sent successfully, or error message string if failed.
    """
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # ✅ Attach resume if provided
    if resume_file is not None:
        part = MIMEApplication(resume_file.read(), Name=resume_file.name)
        part['Content-Disposition'] = f'attachment; filename="{resume_file.name}"'
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)
