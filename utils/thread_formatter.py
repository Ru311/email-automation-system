"""Helpers for turning Gmail messages into AI-friendly text."""

def clean_email_body(body: str) -> str:
    """
    Removes email thread history and quoted text from the email body.
    Strips out: Original Message markers, quoted blocks, and Gmail's "On ... wrote:" patterns.
    """
    lines = body.splitlines()
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()

        if "-----Original Message-----" in stripped:
            break

        if stripped.startswith("-----") and len(stripped) > 5:
            break

        if "wrote:" in stripped:
            for j in range(max(0, i-2), i):
                if "On " in lines[j]:
                    break
            else:
                cleaned_lines.append(line)
                continue
            break

        if stripped.startswith(">"):
            break

        if stripped.startswith("On ") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith("wrote:") or "wrote:" in next_line:
                break

        cleaned_lines.append(line)

    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    cleaned_body = "\n".join(cleaned_lines).strip()
    
    return cleaned_body[:2000]

def format_thread_for_ai(conversation):
    """Format a thread so it can be passed to the classifier."""

    formatted = "EMAIL THREAD\n\n"

    for i, email in enumerate(conversation):

        sender = email["sender"]
        body = clean_email_body(email["body"])
        formatted += f"Message {i+1}\n"
        formatted += f"From: {sender}\n"

        formatted += f"Content:\n{body}\n"
        formatted += "\n---\n\n"

    return formatted

def format_email_for_ai(email):
    """Format a single email so it can be passed to the classifier."""

    formatted = "EMAIL \n\n"

    sender = email["sender"]
    body = email["body"].strip()
    formatted += f"From: {sender}\n"

    formatted += f"Content:\n{body}\n"
    formatted += "\n---\n\n"

    return formatted
