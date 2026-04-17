def format_thread_for_ai(conversation):

    formatted = "EMAIL THREAD\n\n"

    for i, email in enumerate(conversation):

        sender = email["sender"]
        subject = email["subject"]
        body = email["body"].strip()

        formatted += f"Message {i+1}\n"
        formatted += f"From: {sender}\n"

        if subject:
            formatted += f"Subject: {subject}\n"

        formatted += f"Content:\n{body}\n"
        formatted += "\n---\n\n"

    return formatted