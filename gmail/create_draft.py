from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64


def create_draft(service, to_email, subject, body, thread_id,
                 cc_email, original_message_id, reference, attachments):

    message = MIMEMultipart()

    message["to"] = to_email
    message["cc"] = cc_email

    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    message["subject"] = subject

    message["In-Reply-To"] = original_message_id
    message["References"] = reference

    # ✅ Body
    message.attach(MIMEText(body, "plain"))

    # ✅ Attach files
    for att in attachments:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(base64.urlsafe_b64decode(att["data"]))

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{att["filename"]}"'
        )

        message.attach(part)

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    draft = {
        "message": {
            "raw": raw_message,
            "threadId": thread_id
        }
    }

    return service.users().drafts().create(
        userId="me",
        body=draft
    ).execute()