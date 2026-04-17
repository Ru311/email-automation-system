def extract_name(sender):

    if "<" in sender:
        return sender.split("<")[0].strip()

    return sender   

def is_internal_email(sender, company_domains):

    sender = sender.lower()

    for domain in company_domains:
        if domain in sender:
            return True

    return False