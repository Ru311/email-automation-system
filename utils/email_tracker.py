import json
import os

FILE_PATH = "data/processed_emails.json"


def load_processed_emails():

    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:

        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_processed_email(email_id):

    processed = load_processed_emails()

    processed.append(email_id)

    with open(FILE_PATH, "w") as f:
        json.dump(processed, f, indent=2)


def is_processed(email_id):

    processed = load_processed_emails()

    return email_id in processed