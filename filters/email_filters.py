from config import IGNORE_KEYWORDS
from config import RFQ_KEYWORDS

def should_ignore(email_text):

    email_text = email_text.lower()

    for word in IGNORE_KEYWORDS:

        if word in email_text:
            return True

    return False

def contains_rfq_keywords(subject, body):

    text = (subject + " " + body).lower()

    for keyword in RFQ_KEYWORDS:
        if keyword in text:
            return True

    return False