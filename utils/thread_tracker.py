import json
import os

FILE_PATH = "data/processed_threads.json"


def load_processed_threads():

    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as f:
        try:
            return json.load(f)
        except:
            return []


def is_thread_processed(thread_id):

    processed = load_processed_threads()

    return thread_id in processed


def save_processed_thread(thread_id):

    processed = load_processed_threads()

    processed.append(thread_id)

    with open(FILE_PATH, "w") as f:
        json.dump(processed, f, indent=2)