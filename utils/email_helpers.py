def extract_name(sender):
    """Extract the display name from a formatted sender string."""

    if "<" in sender:
        return sender.split("<")[0].strip()

    return sender   

def is_internal_email(sender, company_domains):
    """Return True when the sender belongs to one of the company domains."""

    sender = sender.lower()

    if sender == "sales.north@themarketinghouse.in":
        return False

    for domain in company_domains:
        if domain in sender:
            return True

    return False

def format_email_context(subject, sender):
    """Build a compact log context for an email."""

    subject = subject.replace("\n", " ").strip()
    if len(subject) > 60:
        subject = subject[:57] + "..."
    return f"[#[{sender}] [{subject}]"

def clean_name(name):
    """Normalize a candidate sender name and reject obvious noise."""

    if not name:
        return None

    name = name.strip()

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
    """Return the last message in a conversation, if any."""

    if not conversation:
        return None
    return conversation[-1]

def extract_attachments(service, message):
    """Fetch attachment payloads for a Gmail message."""

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
