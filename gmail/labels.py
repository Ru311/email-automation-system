def get_or_create_label(service, label_name):

    labels = service.users().labels().list(userId="me").execute()

    for label in labels["labels"]:
        if label["name"] == label_name:
            return label["id"]

    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }

    label = service.users().labels().create(
        userId="me",
        body=label_body
    ).execute()

    return label["id"]

def label_thread(service, thread_id, label_id):

    service.users().threads().modify(
        userId="me",
        id=thread_id,
        body={
            "addLabelIds": [label_id]
        }
    ).execute()