from google import genai
import json
import time
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def classify_email(email_text: str) -> dict:

    prompt = f"""
            You are a highly strict email classifier for a manufacturing company.

            Your task is to 
            1. determine whether the email is a **Request for Quotation (RFQ)**.
            2. Extract the sender's name

            ---

            ## Definition of RFQ

            An RFQ is ONLY when:
            - The sender is explicitly asking for price, quotation, estimate, or costing
            - The request is for manufacturing, fabrication, or services

            ---

            ## STRICT RULES

            ### Mark as RFQ ONLY IF:
            - Clear intent to get pricing or quotation
            - Pricing should be only for PCB or Printed Circuit Boards or Boards or Gerber Data
            - Example phrases:
            - "please share quotation"
            - "need pricing"
            - "quote for PCB"
            - "cost for manufacturing"
            - "can you provide estimate"

            ---

            ### Mark as NOT_RFQ if ANY of these apply:
            - Thanking for a quote
            - Reminding about past requests
            - Sending PO, invoice, payment, or confirmation
            - General inquiry without asking price
            - Internal email
            - Vendor communication
            - Job applications
            - Spam / newsletter

            ---

            ## IMPORTANT BEHAVIOR

            - Be CONSERVATIVE → if unsure, return NOT_RFQ
            - Do NOT assume intent
            - Do NOT classify based on keywords alone
            - Focus on intent, not words

            ---
            ---

            ## SENDER NAME EXTRACTION RULES

            - Extract the person's name from signature or email content
            - Prefer names near:
            - "Regards"
            - "Thanks"
            - "Best"
            - Ignore:
            - Company names
            - Email addresses
            - Designations (Manager, Engineer, etc.)
            - Return a clean human name (1-3 words)
            - If not found → return null

            ---
            ## OUTPUT FORMAT (STRICT JSON)

            Return ONLY valid JSON:

            {{
            "is_rfq": true/false,
            "confidence": 0.0 to 1.0,
            "reason": "detailed explanation with evidence from the mail, give exact content",
            "sender_name": "string or null"
            }}

            ---

            ## EMAIL TO CLASSIFY:
            {email_text}
            """

    max_retries = 5

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            text = response.text.strip()

            # Clean possible markdown formatting around JSON.
            if text.startswith("```"):
                text = text.strip("```").replace("json", "").strip()

            result = json.loads(text)

            return {
                "is_rfq": bool(result.get("is_rfq", False)),
                "confidence": float(result.get("confidence", 0.0)),
                "reason": result.get("reason", "No reason provided"),
                "sender_name": result.get("sender_name")
            }

        except Exception as e:
            # Retry transient failures; return a safe "not RFQ" result if all retries fail.
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue

            return {
                "is_rfq": False,
                "confidence": 0.0,
                "reason": f"AI parsing error: {str(e)}",
                "sender_name": None,
            }
