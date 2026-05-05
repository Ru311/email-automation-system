import logging
import sys
import threading
import traceback

from flask import Flask, jsonify

from ai.classifier import classify_email
from config import COMPANY_DOMAINS, USE_AI_CLASSIFICATION
from filters.email_filters import contains_rfq_keywords, should_ignore
from gmail.auth import get_gmail_service
from gmail.fetch_emails import fetch_last_day_emails
from gmail.forward_email import forward_email
from gmail.labels import get_or_create_label, label_thread
from gmail.parse_email import parse_thread
from utils.email_helpers import (
    clean_name,
    extract_name,
    format_email_context,
    get_latest_message,
    is_internal_email,
)
from utils.email_tracker import is_processed, save_processed_email
from utils.thread_formatter import format_thread_for_ai
from utils.thread_tracker import is_thread_processed, save_processed_thread

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
job_lock = threading.Lock()
job_state = {
    "running": False,
}

LABEL_NAME = "AI_HANDLED"


def _get_sender_name(*, ai_sender_name: str | None, sender_email: str) -> str:
    name = clean_name(ai_sender_name)
    if name:
        return name

    # When AI classification is disabled (or doesn't provide a name), fall back to
    # parsing the display name from the sender header.
    parsed = clean_name(extract_name(sender_email))
    return parsed or "Sir"


def main() -> None:

    service = get_gmail_service()
    messages = fetch_last_day_emails(service)
    
    logger.info("Found %s emails", len(messages))
    label_id = get_or_create_label(service, LABEL_NAME)

    rfq_count = 0
    skipped_count = 0
    to_process_count = 0
    processed_count = 0

    for msg in messages:
        thread_id = msg["threadId"]

        if is_thread_processed(thread_id):
            logger.info("[SKIP] Already processed")
            skipped_count += 1
            continue

        message_id = msg["id"]

        if is_processed(message_id):
            logger.info("[SKIP] Already processed")
            skipped_count += 1
            continue
        
        conversation = parse_thread(service, thread_id)
        thread_length = len(conversation)
        latest_email = conversation[-1]
        subject = latest_email["subject"]
        body = latest_email["body"]
        to_email = latest_email["sender"]

        context = format_email_context(subject, to_email)

        if thread_length != 1:
            logger.info(f"[SKIP] thread length - {thread_length} :: {context}")
            skipped_count += 1
            save_processed_thread(thread_id)
            continue

        original_message_id = latest_email["message_id"]

        sender = latest_email["sender"]
        if is_internal_email(sender, COMPANY_DOMAINS):
            logger.info(f"[SKIP] Internal email :: {context}")
            skipped_count += 1
            save_processed_email(message_id)
            continue

        if should_ignore(body):
            logger.info(f"[SKIP]: Finance/newsletter :: {context})")
            skipped_count += 1
            save_processed_email(message_id)
            continue
        logger.info("----------------------------------------------")
        logger.info(f"[PROCESSED]: Passed basic filter :: {context}")
        to_process_count += 1

        if USE_AI_CLASSIFICATION:
            logger.info(f"{context} [AI] Sending email to classifier")

            thread_text = format_thread_for_ai(conversation)
            ai_result = classify_email(thread_text)

            is_rfq = ai_result["is_rfq"]
            ai_reason = ai_result["reason"]

            logger.info(
                f"{context} [AI] RFQ={is_rfq} | Reason={ai_reason}"
            )

        else:
            logger.info(f"{context} [AI Disabled] — using keyword filter")

            if contains_rfq_keywords(subject, body):
                is_rfq = True
                ai_reason = "Keyword match"
            else:
                is_rfq = False
                ai_reason = "No keywords found"

        if not is_rfq:
            logger.info(f"{context} [FAIL] Not an RFQ email")
            logger.info("----------------------------------------------")
            save_processed_email(message_id)
            continue
        logger.info(f"{context} [PASS] RFQ detected → forwarding for review")

        ai_sender_name = None
        if USE_AI_CLASSIFICATION:
            ai_sender_name = ai_result.get("sender_name")
        sender_name = _get_sender_name(ai_sender_name=ai_sender_name, sender_email=sender)

        latest = get_latest_message(conversation)

        logger.info("[THREAD DEBUG] ThreadID=%s In-Reply-To=%s", thread_id, original_message_id)
        logger.info("[THREAD DEBUG] To=%s Subject=%s", sender, subject)

        # Current behavior: forward the latest message for human review and label
        # the thread as handled.
        forward_email(service, latest["gmail_id"], sender_name)
        logger.info("Forwarded email (review flow)")
        label_thread(service, thread_id, label_id)

        save_processed_thread(thread_id)
        logger.info("Thread labeled and marked processed")
        logger.info("----------------------------------------------")
        save_processed_email(latest_email["message_id"])
        rfq_count += 1
        processed_count += 1
    

    logger.info("========== DAILY SUMMARY ==========")
    logger.info(f"Total emails fetched: {len(messages)}")
    logger.info(f"Ignored emails: {skipped_count}")
    logger.info(f"Emails for AI processing: {to_process_count}")
    logger.info(f"RFQ emails detected: {rfq_count}")
    logger.info("===================================")


def _run_main_in_background():
    try:
        logger.info("[TRIGGER] Background automation job started")
        main()
        logger.info("[TRIGGER] Background automation job completed")
    except Exception:
        logger.error("[TRIGGER] Background automation job failed")
        logger.error(traceback.format_exc())
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
    logger.info("Scheduler triggered (HTTP request received)")
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
