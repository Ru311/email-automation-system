from venv import logger

def clean_email_body(body: str) -> str:
    """
    Removes email thread history and quoted text from the email body.
    Strips out: Original Message markers, quoted blocks, and Gmail's "On ... wrote:" patterns.
    """
    lines = body.splitlines()
    cleaned_lines = []
    quote_block_started = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Stop at definitive Outlook marker
        if "-----Original Message-----" in stripped:
            break
        
        # Stop at divider-only lines (multiple dashes)
        if stripped.startswith("-----") and len(stripped) > 5:
            break
        
        # Stop at Gmail's quoted format: "On [date], [name] <email> wrote:"
        # This often spans 1-2 lines, so we check with context
        if "wrote:" in stripped:
            # Look backwards to see if there's an "On" in recent lines
            for j in range(max(0, i-2), i):
                if "On " in lines[j]:
                    break
            else:
                # If we reach here, the "wrote:" is likely just text, not a marker
                cleaned_lines.append(line)
                continue
            break
        
        # Stop when we hit a block of quoted lines (> prefix)
        if stripped.startswith(">"):
            quote_block_started = True
            break
        
        # Also stop at "On ... wrote:" on separate lines
        if stripped.startswith("On ") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith("wrote:") or "wrote:" in next_line:
                break
        
        cleaned_lines.append(line)
    
    # Remove trailing empty lines
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    cleaned_body = "\n".join(cleaned_lines).strip()
    
    return cleaned_body[:2000]

def format_thread_for_ai(conversation):

    formatted = "EMAIL THREAD\n\n"

    for i, email in enumerate(conversation):

        sender = email["sender"]
        subject = email["subject"]
        body = clean_email_body(email["body"])
        formatted += f"Message {i+1}\n"
        formatted += f"From: {sender}\n"

        # if subject:
        #     formatted += f"Subject: {subject}\n"

        formatted += f"Content:\n{body}\n"
        formatted += "\n---\n\n"

        #logger.info(f"{formatted} [AI] Sending email to classifier")

    return formatted

def format_email_for_ai(email):

    formatted = "EMAIL \n\n"

    sender = email["sender"]
    subject = email["subject"]
    body = email["body"].strip()
    formatted += f"From: {sender}\n"

    # if subject:
    #     formatted += f"Subject: {subject}\n"

    formatted += f"Content:\n{body}\n"
    formatted += "\n---\n\n"

    # logger.info(f"[AI] Cleaned body (first 500 chars): {body[:500]}")
    # logger.info(f"{formatted} [AI] Sending email to classifier")

    return formatted