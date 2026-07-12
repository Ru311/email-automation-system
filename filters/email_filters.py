from config import IGNORE_KEYWORDS
from config import RFQ_KEYWORDS
from utils.logger import logger

def should_ignore(email_text):
    """Return True when the text matches a configured ignore keyword."""

    email_text = email_text.lower()

    for word in IGNORE_KEYWORDS:

        if word in email_text:
            logger.info("Ignoring email because it matched keyword: %s", word)
            return True

    return False

def contains_rfq_keywords(subject, body):
    """Return True when the subject or body contains RFQ keywords."""

    text = (subject + " " + body).lower()

    for keyword in RFQ_KEYWORDS:
        if keyword in text:
            return True

    return False
