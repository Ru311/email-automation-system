import base64
from bs4 import BeautifulSoup


def extract_body(payload):

    body = ""

    if "parts" in payload:

        for part in payload["parts"]:

            mime = part.get("mimeType", "")

            # plain text
            if mime == "text/plain":

                data = part["body"].get("data")

                if data:
                    body = base64.urlsafe_b64decode(data).decode(errors="ignore")
                    return body

            # html fallback
            if mime == "text/html":

                data = part["body"].get("data")

                if data:
                    html = base64.urlsafe_b64decode(data).decode(errors="ignore")
                    soup = BeautifulSoup(html, "html.parser")
                    body = soup.get_text()
                    return body

            # recursive search
            if "parts" in part:
                body = extract_body(part)

                if body:
                    return body

    else:

        data = payload["body"].get("data")

        if data:
            body = base64.urlsafe_b64decode(data).decode(errors="ignore")

    return body

def parse_thread(service, thread_id):

    thread = service.users().threads().get(
        userId="me",
        id=thread_id
    ).execute()

    conversation = []
    messages = thread.get("messages", [])

    if not messages:
        return []

    for message in messages:

        headers = message["payload"]["headers"]

        sender = ""
        subject = ""
        to_emails = ""
        cc_emails = ""
        message_id_header = ""

        for h in headers:

            if h["name"].lower() == "from":
                sender = h["value"]

            if h["name"].lower() == "subject":
                subject = h["value"]

            if h["name"].lower() == "to":
                to_emails = h["value"]

            if h["name"].lower() == "cc":
                cc_emails = h["value"]

            if h["name"].lower() == "message-id":
                message_id_header = h["value"]

        body = extract_body(message['payload'])
        if not body:
            continue

        conversation.append({
            "subject": subject,
            "sender": sender,
            "body": body,
            "to": to_emails,
            "cc": cc_emails,
            "message_id": message_id_header
        })
    # print("parse_thread returning:", type(conversation))
    return conversation

def parse_email(service, message_id):

    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = msg['payload']['headers']

    subject = ""
    sender = ""
    to_emails = ""
    cc_emails = ""

    for h in headers:

        if h["name"].lower() == "from":
            sender = h["value"]

        if h["name"].lower() == "subject":
            subject = h["value"]

        if h["name"].lower() == "to":
            to_emails = h["value"]

        if h["name"].lower() == "cc":
            cc_emails = h["value"]

    body = extract_body(msg['payload'])

    return {
        "subject": subject,
        "sender": sender,
        "body": body,
        "to": to_emails,
        "cc": cc_emails
    }