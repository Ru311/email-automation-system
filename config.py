import os
from dotenv import load_dotenv

# Load variables from .env into the environment (safe no-op if .env is absent).
load_dotenv()

# =============================================================================
# config.py — Central configuration for the Email Automation System
# =============================================================================
# All tuneable settings live here so that no magic values are scattered
# across the codebase.  Edit this file to change behaviour without touching
# business logic.
# =============================================================================


# ---------------------------------------------------------------------------
# Gmail OAuth 2.0 scope — "modify" lets us read, label, draft and send email.
# ---------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# ---------------------------------------------------------------------------
# Gemini AI API key — loaded from the .env file, never hardcoded here.
# Set GEMINI_API_KEY=<your_key> in your .env file.
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. "
        "Add it to your .env file: GEMINI_API_KEY=your_key_here"
    )

# ---------------------------------------------------------------------------
# Execution flags
# ---------------------------------------------------------------------------

# When True  → emails are sent immediately via the Gmail API.
# When False → a local draft is created instead (safe for testing).
SEND_EMAILS = False

# When True  → Gemini AI is used to classify each email as RFQ / NOT_RFQ.
# When False → falls back to simple keyword matching (faster, less accurate).
USE_AI_CLASSIFICATION = True

# ---------------------------------------------------------------------------
# Recipients
# ---------------------------------------------------------------------------

# Team members to CC on every automated reply / draft.
# Uncomment additional addresses as needed.
TEAM_CC_EMAIL = [
    # "rvaikar310@gmail.com"
    "dean@cmppcb.com",
    "d.lau@cmppcb.com",
    "sales1@themarketinghouse.in"
    # "girish.vaikar@themarketinghouse.in",
]
DRY_RUN = True
# ---------------------------------------------------------------------------
# Domain filtering
# ---------------------------------------------------------------------------

# Emails sent *from* these domains are treated as internal and skipped.
COMPANY_DOMAINS = [
    "themarketinghouse.in",
    "cmppcb.com",
    "phntechnology.com"
]

# ---------------------------------------------------------------------------
# Keyword lists
# ---------------------------------------------------------------------------

# Emails whose body matches ANY of these keywords are immediately ignored
# (finance noise, newsletters, automated notifications, etc.)
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
    "shipment",
]

# Keywords that indicate the email is (or contains) a Request for Quotation.
# Used as the fallback classifier when USE_AI_CLASSIFICATION is False.
RFQ_KEYWORDS = [
    # ---------- Standard RFQ terminology ----------
    "rfq",
    "request for quotation",
    "quotation",
    "quote",
    "price quote",
    "pricing",
    "price",

    # ---------- Buyer request phrases ----------
    "please quote",
    "can you quote",
    "kindly quote",
    "need quotation",
    "looking for quotation",
    "send quote",
    "provide quote",
    "quotation for",

    # ---------- Pricing / cost language ----------
    "price for",
    "pricing for",
    "cost for",
    "unit price",
    "total cost",
    "estimate cost",
    "estimated cost",

    # ---------- PCB / manufacturing context ----------
    "gerber",
    "gerber files",
    "pcb files",
    "pcb fabrication",
    "pcb manufacturing",
    "pcb assembly",
    "board fabrication",
    "pcb prototype",

    # ---------- Attachment signals ----------
    "attached gerber",
    "attached files",
    "attached design",
    "see attached",
    "please find attached",

    # ---------- Urgency signals ----------
    "urgent quote",
    "urgent pricing",
    "asap quote",
]
