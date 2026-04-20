def forward_email(service, message_id, sender_name):

    import base64
    from email import message_from_bytes
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    from config import TEAM_CC_EMAIL, DRY_RUN

    # =========================
    # STEP 1: GET ORIGINAL MAIL
    # =========================
    original = service.users().messages().get(
        userId="me",
        id=message_id,
        format="raw"
    ).execute()

    mime_bytes = base64.urlsafe_b64decode(original["raw"])
    original_msg = message_from_bytes(mime_bytes)

    # =========================
    # STEP 2: EXTRACT HEADERS
    # =========================
    original_from = original_msg.get("From", "")
    original_to = original_msg.get("To", "")
    original_cc = original_msg.get("Cc", "")
    original_date = original_msg.get("Date", "")
    original_subject = original_msg.get("Subject", "")

    # =========================
    # STEP 3: EXTRACT HTML BODY (IMPORTANT)
    # =========================
    def get_original_html(msg):
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore")
        return None

    def get_plain_fallback(msg):
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return "<pre>" + payload.decode(errors="ignore") + "</pre>"
        return ""

    original_html = get_original_html(original_msg)

    if not original_html:
        original_html = get_plain_fallback(original_msg)

    # =========================
    # STEP 4: CLEAN RECIPIENT SPLIT
    # =========================

    # TO → only original sender (client)
    to_email = original_from

    # CC → original CC + your team
    cc_list = []

    if original_cc:
        cc_list.append(original_cc)

    if isinstance(TEAM_CC_EMAIL, list):
        cc_list.extend(TEAM_CC_EMAIL)
    else:
        cc_list.append(TEAM_CC_EMAIL)

    cc_list = [c for c in cc_list if c]
    cc_email = ", ".join(cc_list)

    # =========================
    # STEP 5: CREATE EMAIL
    # =========================
    message = MIMEMultipart()
    message["To"] = to_email
    message["Cc"] = cc_email
    message["Subject"] = "Fwd: " + original_subject

    # =========================
    # STEP 6: CLEAN HTML FORWARD
    # =========================
    html_body = f"""
    <div style="font-family: Arial, sans-serif; font-size:14px; color:#000;">

        <p>Dear {sender_name} Ji,</p>

        <p>
        Thank you for your email. Mr. Dean from our team will revert to you as soon as possible.
        </p>

        <p>
        Please ensure all necessary specifications are included in your email or Gerber Data, such as laminate thickness, laminate TG, copper thickness, solder mask color, legend color, and final finish. If these details are missing, please provide them promptly to avoid any delay in your quotation.
        </p>

        <br>

        <p>
        Thanks and with Warm Regards,<br><br>

        <strong>Girish Vaikar</strong><br>
        Business Head - Bharat<br>
        CMP Co. Ltd.<br><br>

        <strong>Bharat Office -</strong><br>
        The Marketing House<br>
        Office No 68, Rahul Complex, Near Anand Nagar Metro Station,<br>
        Poud Road, Kothrud, Pune 411038 (Bharat)<br><br>

        Mob - +91-9822047401<br>
        Email - girish.vaikar@themarketinghouse.in
        </p>

        <br>

        <div style="border-top:1px solid #ccc; padding-top:10px; margin-top:20px; font-size:13px;">
            <b>---------- Forwarded message ---------</b><br>
            <b>From:</b> {original_from}<br>
            <b>Date:</b> {original_date}<br>
            <b>Subject:</b> {original_subject}<br>
            <b>To:</b> {original_to}<br>
        </div>

        <br>

        <div>
            {original_html}
        </div>
    </div>
    """

    message.attach(MIMEText(html_body, "html"))

    # =========================
    # STEP 7: ADD ATTACHMENTS
    # =========================
    from email.mime.base import MIMEBase
    from email import encoders

    for part in original_msg.walk():

        content_disposition = str(part.get("Content-Disposition", ""))

        if "attachment" in content_disposition:

            filename = part.get_filename()
            payload = part.get_payload(decode=True)

            if not payload:
                continue

            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(payload)

            encoders.encode_base64(attachment)

            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"'
            )

            message.attach(attachment)

    # =========================
    # STEP 7: ENCODE
    # =========================
    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    # =========================
    # STEP 8: DRY RUN SAFETY
    # =========================
    if DRY_RUN:
        return service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}}
        ).execute()
    else:
        return service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()