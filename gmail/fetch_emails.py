from datetime import datetime, timedelta
import time


def fetch_last_day_emails(service):

    five_minutes_ago = int(time.time()) - 300

    query = f"""
        after:{five_minutes_ago}
        -category:promotions
        -category:social
        -category:updates
        -from:noreply
        -from:no-reply
        """
   
    results = service.users().messages().list(
            userId="me",
            q=query
        ).execute()

    messages = results.get("messages", [])

    return messages