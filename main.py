import threading
import traceback

from gmail import forward_email
from gmail.auth import get_gmail_service
from gmail.fetch_emails import fetch_last_day_emails
from gmail.parse_email import parse_thread
from utils.logger import logger
from filters.email_filters import should_ignore, contains_rfq_keywords
from utils.thread_formatter import format_thread_for_ai
from ai.classifier import classify_email
from utils.email_tracker import is_processed, save_processed_email
from utils.thread_tracker import is_thread_processed, save_processed_thread
from utils.reply_template import generate_reply
from utils.email_helpers import extract_attachments, extract_name, is_internal_email, format_email_context, clean_name, get_latest_message
from gmail.create_draft import create_draft
from gmail.send_reply import send_reply
from gmail.labels import get_or_create_label, label_thread
from config import TEAM_CC_EMAIL, SEND_EMAILS, COMPANY_DOMAINS
from utils.email_participants import merge_cc
from config import USE_AI_CLASSIFICATION
from gmail.forward_email import forward_email
import time
from flask import Flask, jsonify

app = Flask(__name__)
job_lock = threading.Lock()
job_state = {
    "running": False,
}

def main():

    service = get_gmail_service()

    messages = fetch_last_day_emails(service)

    print(f"Found {len(messages)} emails")
    
    label_id = get_or_create_label(service, "AI_HANDLED")

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
        
        thread_id = msg["threadId"]
        conversation = parse_thread(service, thread_id)
        thread_length = len(conversation)
        latest_email = conversation[-1]
        subject = latest_email["subject"]
        body = latest_email["body"]
        to_email = latest_email["sender"]
        original_cc = latest_email["cc"]        
        cc_list = merge_cc(original_cc, TEAM_CC_EMAIL)

        context = format_email_context(subject,to_email)

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

        # Later AI classifier will go here
        # if USE_AI_CLASSIFICATION:
        #     logger.info("Sending email to AI classifier")
        #     thread_text = format_thread_for_ai(conversation)
        #     thread_text = thread_text[:8000]
        #     classification = classify_email(thread_text)

        # else:

        #     logger.info("AI disabled — using keyword filter only")
        #     if contains_rfq_keywords(subject, body):
        #         classification = "RFQ"
        #     else:
        #         classification = "NOT_RFQ"

        # logger.info(f"AI classification result: {classification}")

        # if classification != "RFQ":

        #     logger.info("[FAIL]: Not an RFQ email")
        #     logger.info("----------------------------------------------")
        #     save_processed_email(message_id)
        #     continue

        # logger.info("[PASS]: RFQ detected - creating draft")

        CONFIDENCE_THRESHOLD = 0.85

        if USE_AI_CLASSIFICATION:
            logger.info(f"{context} [AI] Sending email to classifier")

            thread_text = format_thread_for_ai(conversation)
            # thread_text = clean_email(thread_text)[:8000]

            ai_result = classify_email(thread_text)

            is_rfq = ai_result["is_rfq"]
            confidence = ai_result["confidence"]
            ai_reason = ai_result["reason"]

            logger.info(
                f"{context} [AI] RFQ={is_rfq} | Conf={confidence:.2f} | Reason={ai_reason}"
            )

        else:
            logger.info(f"{context} [AI Disabled] — using keyword filter")

            if contains_rfq_keywords(subject, body):
                is_rfq = True
                confidence = 0.6
                ai_reason = "Keyword match"
            else:
                is_rfq = False
                confidence = 0.0
                ai_reason = "No keywords found"

        # 🎯 DECISION LOGIC
        if not is_rfq:
            action = "SKIP"
            reason = "NotRFQ"

        elif confidence >= CONFIDENCE_THRESHOLD:
            action = "SEND"
            reason = "HighConfidence"

        else:
            action = "DRAFT"
            reason = "LowConfidence"

        logger.info(
            f"{context} [RESULT] Action={action} | Conf={confidence:.2f} | Reason={reason}"
        )

        # 🚀 APPLY ACTION
        if action == "SKIP":
            logger.info(f"{context} [FAIL] Not an RFQ email")
            logger.info("----------------------------------------------")
            save_processed_email(message_id)
            continue

        elif action == "DRAFT":
            logger.info(f"{context} [PASS] RFQ detected (low confidence) → creating draft")
            # create_draft(...)   # your existing function

        elif action == "SEND":
            logger.info(f"{context} [PASS] RFQ detected (high confidence) → sending email")
            # send_email(...)     # your existing function

        sender_name = clean_name(ai_result.get("sender_name"))
        if not sender_name:
            sender_name = "Sir"
        reply_body = generate_reply(sender_name)

        to_email = sender
        latest = get_latest_message(conversation)
        attachments = extract_attachments(service, latest)
        message_id = latest["message_id"]
        references = latest.get("references", "")
        if references:
            references = references + " " + message_id
        else:
            references = message_id

        logger.info(f"[THREAD DEBUG]")
        logger.info(f"Thread ID: {thread_id}")
        logger.info(f"In-Reply-To: {original_message_id}")
        logger.info(f"References: {references}")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message-ID: {message_id}")

        # if SEND_EMAILS:
        #     send_reply(
        #         service,
        #         to_email,
        #         subject,
        #         reply_body,
        #         thread_id,
        #         cc_list,
        #         message_id,
        #         references,
        #         attachments
        #     )

        #     logger.info("Email sent automatically")

        # else:
        #     create_draft(
        #         service,
        #         to_email,
        #         subject,
        #         reply_body,
        #         thread_id,
        #         cc_list,
        #         message_id,
        #         references,
        #         attachments
        #     )
        #     logger.info("Draft created (testing mode)")

        forward_email(
                        service,
                        latest["gmail_id"],
                        sender_name
                    )
        logger.info("Draft created (testing mode)")
        label_thread(service, thread_id, label_id)

        save_processed_thread(thread_id)
        logger.info("Draft created and thread labeled")
        logger.info("----------------------------------------------")
        save_processed_email(message_id)
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
