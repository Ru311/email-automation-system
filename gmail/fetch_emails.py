from datetime import datetime, timedelta
import time


def fetch_last_day_emails(service):

    twenty_four_hours_ago = int(time.time()) - 86400

    query = f"""
        after:{twenty_four_hours_ago}
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