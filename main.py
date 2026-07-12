import threading

from flask import Flask, jsonify

from ai.classifier import classify_email
from config import COMPANY_DOMAINS, USE_AI_CLASSIFICATION
from databse.insert_msg_id import mark_processed
from filters.email_filters import should_ignore
from gmail.auth import get_gmail_service
from gmail.fetch_emails import fetch_last_day_emails
from gmail.forward_email import forward_email
from gmail.labels import get_or_create_label, label_thread
from gmail.parse_email import parse_email, parse_thread
from utils.email_helpers import (
    clean_name,
    extract_name,
    format_email_context,
    is_internal_email,
)
from utils.email_tracker import is_processed, save_processed_email
from utils.thread_formatter import format_email_for_ai
from utils.thread_tracker import is_thread_processed, save_processed_thread
from utils.logger import logger

app = Flask(__name__)
job_lock = threading.Lock()
job_state = {
    "running": False,
}

PROCESSED_LABEL_NAME = "AI_HANDLED"
REVIEW_LABEL_NAME = "REVIEW_NEEDED"


def _get_sender_name(*, ai_sender_name: str | None, sender_email: str) -> str:
    """Return the best available display name for a sender."""
    name = clean_name(ai_sender_name)
    if name:
        return name

    parsed = clean_name(extract_name(sender_email))
    return parsed or "Sir"


def main() -> None:
    """Process recent inbox emails and apply the RFQ workflow."""

    service = get_gmail_service()
    messages = fetch_last_day_emails(service)

    logger.info("Found %s emails", len(messages))
    processed_label_id = get_or_create_label(service, PROCESSED_LABEL_NAME)
    review_label_id = get_or_create_label(service, REVIEW_LABEL_NAME)

    for msg in messages:
        thread_id = msg["threadId"]

        if is_thread_processed(thread_id):
            logger.info("[SKIP] Already processed")
            continue

        message_id = msg["id"]

        inserted = mark_processed(message_id, thread_id)

        if not inserted:
            logger.info("[SKIP] Already processed")
            continue

        if is_processed(message_id):
            logger.info("[SKIP] Already processed")
            continue
        
        conversation = parse_thread(service, thread_id)
        email = parse_email(service, message_id)
        thread_length = len(conversation)
        subject = email["subject"]
        body = email["body"]
        sender_email = email["sender"]
        original_message_id = email.get("message_id")

        context = format_email_context(subject, sender_email)

        if thread_length != 1:
            if subject == "CMP PCB - Your Trusted PCB Partner" and thread_length < 3:
                logger.info("[INFO] Thread with Exhbition :: %s", context)
            else:
                logger.info("[SKIP] thread length - %s :: %s", thread_length, context)
                save_processed_thread(thread_id)
                continue

        if is_internal_email(sender_email, COMPANY_DOMAINS):
            logger.info("[SKIP] Internal email :: %s", context)
            save_processed_email(message_id)
            continue

        if should_ignore(body):
            logger.info("%s", body)
            logger.info("[SKIP]: Finance/newsletter :: %s", context)
            save_processed_email(message_id)
            continue

        logger.info("----------------------------------------------")
        logger.info("[PROCESSED]: Passed basic filter :: %s", context)

        ai_result = None
        if USE_AI_CLASSIFICATION:
            logger.info("%s [AI] Sending email to classifier", context)

            email_text = format_email_for_ai(email)
            ai_result = classify_email(email_text)

            is_rfq = ai_result["is_rfq"]
            ai_reason = ai_result["reason"]

            logger.info("%s [AI] RFQ=%s | Reason=%s", context, is_rfq, ai_reason)

        if not is_rfq:
            logger.info("%s [FAIL] Not an RFQ email", context)
            logger.info("----------------------------------------------")
            save_processed_email(message_id)
            continue
        logger.info("%s [PASS] RFQ detected -> forwarding for review", context)

        ai_sender_name = None
        if USE_AI_CLASSIFICATION:
            ai_sender_name = ai_result.get("sender_name") if ai_result else None
        sender_name = _get_sender_name(
            ai_sender_name=ai_sender_name,
            sender_email=sender_email,
        )


        logger.info("[THREAD DEBUG] ThreadID=%s In-Reply-To=%s", thread_id, original_message_id)
        logger.info("[THREAD DEBUG] To=%s Subject=%s", sender_email, subject)


        forward_email(service, message_id, sender_name)
        logger.info("Forwarded email (review flow)")

        label_thread(service, thread_id, processed_label_id)

        save_processed_thread(thread_id)
        logger.info("Thread labeled and marked processed")
        logger.info("----------------------------------------------")
        save_processed_email(message_id)

def _run_main_in_background():
    try:
        main()
    except Exception:
        logger.error("Automation failed")
    finally:
        with job_lock:
            job_state["running"] = False


def start_background_job():
    with job_lock:
        if job_state["running"]:
            return False

        job_state["running"] = True

    worker = threading.Thread(target=_run_main_in_background, daemon=True)
    worker.start()
    return True


@app.route("/", methods=["GET"])
def run():
    """Run the email processing job once via HTTP."""
    started = start_background_job()

    if started:
        return jsonify({
            "status": "accepted",
            "message": "Automation triggered successfully. Processing continues in background.",
        }), 202

    return jsonify({
        "status": "already_running",
        "message": "Automation is already processing in background.",
    }), 202

if __name__ == "__main__":
    main()
