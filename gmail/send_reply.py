import base64
from email.mime.text import MIMEText


def send_reply(service, to_email, subject, body, thread_id, cc_email, original_message_id):

    message = MIMEText(body)

    message["to"] = to_email
    message["cc"] = cc_email
    
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject
    message["subject"] = subject

    message["In-Reply-To"] = original_message_id
    message["References"] = original_message_id

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    message_body = {
        "raw": raw_message,
        "threadId": thread_id
    }

    service.users().messages().send(
        userId="me",
        body=message_body
    ).execute()