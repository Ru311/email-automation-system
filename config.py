SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
GEMINI_API_KEY = "AIzaSyDrXyy_ii56ApYmVs1k61J4qKCcxX_nQ6s"
SEND_EMAILS = False
USE_AI_CLASSIFICATION = True
TEAM_CC_EMAIL = [
    # "dean@cmppcb.com",
    # "d.lau@cmppcb.com",
    # "sales1@themarketinghouse.in",
    "girish.vaikar@themarketinghouse.in"
]

COMPANY_DOMAINS = [
    "themarketinghouse.in",
    "cmppcb.com"
]

RFQ_KEYWORDS = [
    "rfq",
    "quotation",
    "quote",
    "pricing",
    "proposal"
]

IGNORE_KEYWORDS = [
    "invoice",
    "payment",
    "bank",
    "statement",
    "newsletter",
    "unsubscribe",
    "LinkedIn",
    "noreply",
    "do not reply",
    "password",
    "OTP",
    "tracking",
    "shipment"
]

RFQ_KEYWORDS = [
    # RFQ terminology
    "rfq",
    "request for quotation",
    "quotation",
    "quote",
    "price quote",
    "pricing",
    "price"

    # buyer requests
    "please quote",
    "can you quote",
    "kindly quote",
    "need quotation",
    "looking for quotation",
    "send quote",
    "provide quote",
    "quotation for",

    # pricing language
    "price for",
    "pricing for",
    "cost for",
    "unit price",
    "total cost",
    "estimate cost",
    "estimated cost",

    # PCB / manufacturing context
    "gerber",
    "gerber files",
    "pcb files",
    "pcb fabrication",
    "pcb manufacturing",
    "pcb assembly",
    "board fabrication",
    "pcb prototype",

    # attachment signals
    "attached gerber",
    "attached files",
    "attached design",
    "see attached",
    "please find attached",

    # urgency signals
    "urgent quote",
    "urgent pricing",
    "asap quote"
]
