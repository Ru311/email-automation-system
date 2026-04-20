def extract_name(sender):

    if "<" in sender:
        return sender.split("<")[0].strip()

    return sender   

def is_internal_email(sender, company_domains):

    sender = sender.lower()

    for domain in company_domains:
        if domain in sender:
            return True

    return False

def format_email_context(subject, sender):
    subject = subject.replace("\n", " ").strip()
    if len(subject) > 60:
        subject = subject[:57] + "..."
    return f"[#[{sender}] [{subject}]"

def clean_name(name):
    if not name:
        return None

    name = name.strip()

    # reject garbage
    if "@" in name:
        return None
    if len(name) > 40:
        return None
    if any(char.isdigit() for char in name):
        return None

    words = name.split()

    if 1 <= len(words) <= 3:
        return name

    return None

def get_latest_message(conversation):
    if not conversation:
        return None
    return conversation[-1]

def extract_attachments(service, message):
    attachments = []

    payload = message.get("payload", {})
    parts = payload.get("parts", [])

    for part in parts:
        filename = part.get("filename")
        body = part.get("body", {})

        if filename and body.get("attachmentId"):
            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=message["id"],
                id=body["attachmentId"]
            ).execute()

            data = attachment.get("data")
            attachments.append({
                "filename": filename,
                "data": data
            })

    return attachments