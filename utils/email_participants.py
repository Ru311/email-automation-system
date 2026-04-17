def merge_cc(original_cc, team_cc_list):

    cc_list = []

    if original_cc:
        original_list = [email.strip() for email in original_cc.split(",")]
        cc_list.extend(original_list)

    for email in team_cc_list:
        if email not in cc_list:
            cc_list.append(email)

    return ", ".join(cc_list)