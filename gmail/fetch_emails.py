from datetime import datetime, timedelta
import time


def fetch_last_day_emails(service):

    one_minutes_ago = int(time.time()) - 60

    query = f"""
        in:inbox
        after:{one_minutes_ago}
        -category:promotions
        -category:social
        -category:updates
        -from:noreply
        -from:no-reply
        """
    # query = 'subject:"RE: RE: RFQ - Series - CCM - U171 - Bare PCB"'
   
    results = service.users().messages().list(
            userId="me",
            q=query
        ).execute()

    messages = results.get("messages", [])

    return messages