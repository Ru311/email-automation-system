import textwrap

def generate_reply(sender_name):

    return textwrap.dedent(f"""\
Dear {sender_name} Ji,

Thank you for your RFQ. Mr. Dean from our team will revert to you as soon as possible.

Please ensure all necessary specifications are included in your email or Gerber Data, such as laminate thickness, laminate TG, copper thickness, solder mask color, legend color, and final finish. If these details are missing, please provide them promptly to avoid any delay in your quotation.


Thanks and with Warm Regards,

Girish Vaikar

Business Head - Bharat 
CMP Co. Ltd.

Bharat Office - 
​The Marketing House
Office No 68, Rahul Complex , Near Anand Nagar Metro Station , Poud Road, Kothrud , Pune 411038 ( Bharat )
Mob - +91-9822047401
Email - girish.vaikar@themarketinghouse.in


""").strip()