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
from utils.email_helpers import extract_name, is_internal_email
from gmail.create_draft import create_draft
from gmail.send_reply import send_reply
from gmail.labels import get_or_create_label, label_thread
from config import TEAM_CC_EMAIL, SEND_EMAILS, COMPANY_DOMAINS
from utils.email_participants import merge_cc
from config import USE_AI_CLASSIFICATION
import time

def main():

    service = get_gmail_service()

    messages = fetch_last_day_emails(service)

    print(f"Found {len(messages)} emails")
    
    label_id = get_or_create_label(service, "AI_HANDLED")

    rfq_count = 0
    ignored_count = 0
    to_process_count = 0
    MAX_EMAILS_PER_MINUTE = 5
    processed_count = 0

    for msg in messages:

        if processed_count >= MAX_EMAILS_PER_MINUTE:
            logger.info("Reached processing limit. Sleeping for 60 seconds...")
            time.sleep(60)
            processed_count = 0

        thread_id = msg["threadId"]

        if is_thread_processed(thread_id):

            logger.info("Skipping thread already handled by team")
            continue

        message_id = msg["id"]

        if is_processed(message_id):

            logger.info("Skipping already processed email")
            continue
        
        thread_id = msg["threadId"]

        conversation = parse_thread(service, thread_id)

        thread_length = len(conversation)

        if thread_length != 1:
            logger.info(f"Skipping thread with {thread_length} messages (ongoing conversation)")
            save_processed_thread(thread_id)
            continue

        latest_email = conversation[-1]
        original_message_id = latest_email["message_id"]
        to_email = latest_email["sender"]
        original_cc = latest_email["cc"]        
        cc_list = merge_cc(original_cc, TEAM_CC_EMAIL)

        sender = latest_email["sender"]
        if is_internal_email(sender, COMPANY_DOMAINS):
            logger.info("Skipping internal email")
            save_processed_email(message_id)
            continue
        subject = latest_email["subject"]
        body = latest_email["body"]

        logger.info("----- NEW EMAIL THREAD -----")
        logger.info(f"From: {sender}")
        logger.info(f"Subject: {subject}")

        if should_ignore(body):
            ignored_count += 1

            logger.info("Status: Ignored (finance/newsletter filter)")
            logger.info("-----------------------------")
            save_processed_email(message_id)
            continue

        # if not contains_rfq_keywords(subject, body):
        #     ignored_count += 1

        #     logger.info("Skipping - no RFQ keywords detected")
        #     save_processed_email(message_id)
        #     continue

        # logger.info(f"Keyword RFQ detected: {contains_rfq_keywords(subject, body)}")
        logger.info("Status: Passed basic filter")
        to_process_count += 1

        # Later AI classifier will go here
        if USE_AI_CLASSIFICATION:

            logger.info("Sending email to AI classifier")

            thread_text = format_thread_for_ai(conversation)
            thread_text = thread_text[:8000]

            classification = classify_email(thread_text)

        else:

            logger.info("AI disabled — using keyword filter only")

            if contains_rfq_keywords(subject, body):
                classification = "RFQ"
            else:
                classification = "NOT_RFQ"

        logger.info(f"AI classification result: {classification}")

        if classification != "RFQ":

            logger.info("Status: Not an RFQ email")
            logger.info("-----------------------------")
            save_processed_email(message_id)
            continue

        logger.info("Status: RFQ detected - creating draft")

        sender_name = extract_name(sender)

        reply_body = generate_reply(sender_name)

        to_email = sender

        if SEND_EMAILS:
            send_reply(
                service,
                to_email,
                subject,
                reply_body,
                thread_id,
                cc_list,
                original_message_id
            )

            logger.info("Email sent automatically")

        else:
            create_draft(
                service,
                to_email,
                subject,
                reply_body,
                thread_id,
                cc_list,
                original_message_id
            )
            logger.info("Draft created (testing mode)")

        label_thread(service, thread_id, label_id)

        save_processed_thread(thread_id)
        logger.info("Draft created and thread labeled")
        save_processed_email(message_id)
        rfq_count += 1
        processed_count += 1
    

    logger.info("========== DAILY SUMMARY ==========")
    logger.info(f"Total emails fetched: {len(messages)}")
    logger.info(f"Ignored emails: {ignored_count}")
    logger.info(f"Emails for AI processing: {to_process_count}")
    logger.info(f"RFQ emails detected: {rfq_count}")
    logger.info("===================================")


if __name__ == "__main__":
    main()